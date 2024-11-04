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
