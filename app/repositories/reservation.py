"""Reservation repository with overlap-detection queries."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Select, and_, select

from app.enums import ReservationStatus
from app.models.reservation import Reservation, ReservationLine
from app.repositories.base import BaseRepository

# Statuses that still hold inventory and therefore block overlapping windows.
BLOCKING_STATUSES = (
    ReservationStatus.PENDING,
    ReservationStatus.CONFIRMED,
    ReservationStatus.PICKED_UP,
    ReservationStatus.OVERDUE,
)


class ReservationRepository(BaseRepository[Reservation]):
    model = Reservation

    def get_by_reference(self, reference: str) -> Reservation | None:
        stmt = select(Reservation).where(Reservation.reference == reference)
        return self.session.execute(stmt).scalar_one_or_none()

    def search_query(
        self,
        customer_id: int | None = None,
        status: ReservationStatus | None = None,
    ) -> Select:
        stmt = select(Reservation)
        if customer_id is not None:
            stmt = stmt.where(Reservation.customer_id == customer_id)
        if status is not None:
            stmt = stmt.where(Reservation.status == status)
        return stmt.order_by(Reservation.starts_at.desc())
