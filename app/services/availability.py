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
