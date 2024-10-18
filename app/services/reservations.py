"""Reservation service: availability, lifecycle, and inventory holds."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.enums import (
    RESERVATION_TRANSITIONS,
    AssetStatus,
    CustomerStatus,
    ReservationStatus,
    can_transition,
)
from app.errors import (
    BusinessRuleError,
    ConflictError,
    InvalidStateError,
    NotFoundError,
    ValidationError,
)
from app.events import EventType, emit_event, envelope
from app.models.reservation import Reservation, ReservationLine
from app.pagination import Page, PageParams, paginate
from app.repositories.catalog import AssetRepository
from app.repositories.customer import CustomerRepository
from app.repositories.reservation import ReservationRepository
from app.services.audit import record_audit
from app.services.references import next_reservation_reference


class ReservationService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = ReservationRepository(session)
        self.assets = AssetRepository(session)
        self.customers = CustomerRepository(session)

    def check_availability(
        self,
        asset_id: int,
        starts_at: datetime,
        ends_at: datetime,
        exclude_reservation_id: int | None = None,
    ) -> list[int]:
        """Return the ids of reservations that conflict over the window."""

        if ends_at <= starts_at:
            raise ValidationError("ends_at must be after starts_at")
        return self.repo.overlapping_line_ids(
            asset_id, starts_at, ends_at, exclude_reservation_id
        )

    def is_available(self, asset_id: int, starts_at: datetime, ends_at: datetime) -> bool:
        return not self.check_availability(asset_id, starts_at, ends_at)

    def create(self, data: dict, actor_id: int | None = None) -> Reservation:
        customer = self.customers.get_active(data["customer_id"])
        if customer is None:
            raise NotFoundError(f"customer {data['customer_id']} not found")
        if customer.status in (CustomerStatus.BLOCKED, CustomerStatus.ARCHIVED):
            raise BusinessRuleError(f"customer is {customer.status} and cannot reserve")

        starts_at = data["starts_at"]
        ends_at = data["ends_at"]
        if ends_at <= starts_at:
            raise ValidationError("ends_at must be after starts_at")

        lines = data["lines"]
        self._validate_lines_available(lines, starts_at, ends_at)

        reservation = Reservation(
            reference=next_reservation_reference(self.session),
            customer_id=customer.id,
            created_by_id=actor_id,
            starts_at=starts_at,
            ends_at=ends_at,
            notes=data.get("notes"),
        )
        for line in lines:
            reservation.lines.append(
                ReservationLine(
                    asset_id=line["asset_id"],
                    kit_id=line.get("kit_id"),
                    quantity=line.get("quantity", 1),
                )
            )
        self.repo.add(reservation)
        record_audit(
            self.session,
            actor_id=actor_id,
            action="reservation.created",
            entity_type="reservation",
            entity_id=reservation.id,
            payload={"reference": reservation.reference},
        )
        emit_event(
            self.session,
            EventType.RESERVATION_CREATED,
            envelope(
                EventType.RESERVATION_CREATED,
                "reservation",
                reservation.id,
                reference=reservation.reference,
                customer_id=reservation.customer_id,
            ),
        )
        return reservation

    def _validate_lines_available(self, lines: list[dict], starts_at, ends_at) -> None:
        seen: set[int] = set()
        for line in lines:
            asset_id = line["asset_id"]
            if asset_id in seen:
                raise ValidationError(f"asset {asset_id} appears more than once")
            seen.add(asset_id)
            asset = self.assets.get(asset_id)
            if asset is None or asset.deleted_at is not None:
                raise NotFoundError(f"asset {asset_id} not found")
            if asset.status in (AssetStatus.RETIRED, AssetStatus.LOST):
                raise BusinessRuleError(f"asset {asset_id} is {asset.status}")
            conflicts = self.check_availability(asset_id, starts_at, ends_at)
            if conflicts:
                raise ConflictError(
                    f"asset {asset_id} is unavailable for the requested window",
                    details={"conflicting_reservation_ids": conflicts},
                )

    def get(self, reservation_id: int) -> Reservation:
        reservation = self.repo.get(reservation_id)
        if reservation is None:
            raise NotFoundError(f"reservation {reservation_id} not found")
        return reservation

    def _transition(self, reservation: Reservation, target: ReservationStatus) -> None:
        if not can_transition(RESERVATION_TRANSITIONS, reservation.status, target):
            raise InvalidStateError(
                f"cannot move reservation from {reservation.status} to {target}"
            )
        reservation.status = target

    def confirm(self, reservation_id: int, actor_id: int | None = None) -> Reservation:
        reservation = self.get(reservation_id)
        self._transition(reservation, ReservationStatus.CONFIRMED)
        for line in reservation.lines:
            self._mark_asset(line.asset_id, AssetStatus.RESERVED)
        self.session.flush()
        record_audit(
            self.session,
            actor_id=actor_id,
            action="reservation.confirmed",
            entity_type="reservation",
            entity_id=reservation.id,
        )
        emit_event(
            self.session,
            EventType.RESERVATION_CONFIRMED,
            envelope(EventType.RESERVATION_CONFIRMED, "reservation", reservation.id),
        )
        return reservation

    def cancel(self, reservation_id: int, actor_id: int | None = None) -> Reservation:
        reservation = self.get(reservation_id)
        self._transition(reservation, ReservationStatus.CANCELLED)
        for line in reservation.lines:
            self._release_asset(line.asset_id)
        self.session.flush()
        record_audit(
            self.session,
            actor_id=actor_id,
            action="reservation.cancelled",
            entity_type="reservation",
            entity_id=reservation.id,
        )
        return reservation

    def reschedule(self, reservation_id: int, starts_at: datetime, ends_at: datetime) -> Reservation:
        reservation = self.get(reservation_id)
        if reservation.status not in (ReservationStatus.PENDING, ReservationStatus.CONFIRMED):
            raise InvalidStateError("only pending or confirmed reservations can be rescheduled")
        if ends_at <= starts_at:
            raise ValidationError("ends_at must be after starts_at")
        for line in reservation.lines:
            conflicts = self.check_availability(
                line.asset_id, starts_at, ends_at, exclude_reservation_id=reservation.id
            )
            if conflicts:
                raise ConflictError(
                    f"asset {line.asset_id} is unavailable for the new window",
                    details={"conflicting_reservation_ids": conflicts},
                )
        reservation.starts_at = starts_at
        reservation.ends_at = ends_at
        self.session.flush()
        return reservation

    def mark_no_show(self, reservation_id: int) -> Reservation:
        reservation = self.get(reservation_id)
        self._transition(reservation, ReservationStatus.NO_SHOW)
        for line in reservation.lines:
            self._release_asset(line.asset_id)
        self.session.flush()
        return reservation

    def _mark_asset(self, asset_id: int, status: AssetStatus) -> None:
        asset = self.assets.get(asset_id)
        if asset is not None:
            asset.status = status

    def _release_asset(self, asset_id: int) -> None:
        asset = self.assets.get(asset_id)
        if asset is not None and asset.status in (AssetStatus.RESERVED, AssetStatus.CHECKED_OUT):
            asset.status = AssetStatus.AVAILABLE

    def search(
        self,
        params: PageParams,
        customer_id: int | None = None,
        status: ReservationStatus | None = None,
    ) -> Page:
        stmt = self.repo.search_query(customer_id, status)
        return paginate(self.session, stmt, params)
