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
