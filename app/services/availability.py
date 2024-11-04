"""Availability-calendar service.

Builds a per-asset view of the booked intervals over a window so the front
desk can see at a glance when a piece of gear is free. This is read-only and
sits on top of the same blocking-status rules used to reject double bookings.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from sqlalchemy import and_, select
from sqlalchemy.orm import Session

from app.errors import NotFoundError, ValidationError
from app.models.reservation import Reservation, ReservationLine
from app.repositories.catalog import AssetRepository
from app.repositories.reservation import BLOCKING_STATUSES


@dataclass(slots=True)
class BookedInterval:
    reservation_id: int
    reference: str
    starts_at: datetime
    ends_at: datetime
    status: str


@dataclass(slots=True)
class AssetCalendar:
    asset_id: int
    asset_name: str
    window_start: datetime
    window_end: datetime
    intervals: list[BookedInterval] = field(default_factory=list)

    @property
    def is_free(self) -> bool:
        return not self.intervals

    def to_dict(self) -> dict:
        return {
            "asset_id": self.asset_id,
            "asset_name": self.asset_name,
            "window_start": self.window_start,
            "window_end": self.window_end,
            "is_free": self.is_free,
            "intervals": [
                {
                    "reservation_id": i.reservation_id,
                    "reference": i.reference,
                    "starts_at": i.starts_at,
                    "ends_at": i.ends_at,
                    "status": i.status,
                }
                for i in self.intervals
            ],
        }


class AvailabilityService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.assets = AssetRepository(session)

    def asset_calendar(
        self, asset_id: int, window_start: datetime, window_end: datetime
    ) -> AssetCalendar:
        if window_end <= window_start:
            raise ValidationError("window_end must be after window_start")
        asset = self.assets.get(asset_id)
        if asset is None or asset.deleted_at is not None:
            raise NotFoundError(f"asset {asset_id} not found")

        stmt = (
            select(Reservation)
            .join(ReservationLine, ReservationLine.reservation_id == Reservation.id)
            .where(
                and_(
                    ReservationLine.asset_id == asset_id,
                    Reservation.status.in_(BLOCKING_STATUSES),
                    Reservation.starts_at < window_end,
                    window_start < Reservation.ends_at,
                )
            )
            .order_by(Reservation.starts_at)
        )
        reservations = self.session.execute(stmt).scalars().all()
        calendar = AssetCalendar(
            asset_id=asset.id,
            asset_name=asset.name,
            window_start=window_start,
            window_end=window_end,
        )
        for res in reservations:
            calendar.intervals.append(
                BookedInterval(
                    reservation_id=res.id,
                    reference=res.reference,
                    starts_at=res.starts_at,
                    ends_at=res.ends_at,
                    status=str(res.status),
                )
            )
        return calendar
