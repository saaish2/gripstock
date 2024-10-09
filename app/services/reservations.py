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
