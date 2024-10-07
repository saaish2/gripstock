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

    def overlapping_line_ids(
        self,
        asset_id: int,
        starts_at: datetime,
        ends_at: datetime,
        exclude_reservation_id: int | None = None,
    ) -> list[int]:
        """Return reservation ids that hold ``asset_id`` over the window.

        Two half-open intervals ``[a_start, a_end)`` and ``[b_start, b_end)``
        overlap iff ``a_start < b_end and b_start < a_end``.
        """

        stmt = (
            select(Reservation.id)
            .join(ReservationLine, ReservationLine.reservation_id == Reservation.id)
            .where(
                and_(
                    ReservationLine.asset_id == asset_id,
                    Reservation.status.in_(BLOCKING_STATUSES),
                    Reservation.starts_at < ends_at,
                    starts_at < Reservation.ends_at,
                )
            )
        )
        if exclude_reservation_id is not None:
            stmt = stmt.where(Reservation.id != exclude_reservation_id)
        return list(self.session.execute(stmt).scalars().all())
