"""Periodic sweeps run by the scheduler/cron.

Each sweep is a pure function over a session so it can be invoked from a cron
entry, a management command, or a test. They return a small summary dict that
the caller can log or surface on an ops dashboard.
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.enums import ReservationStatus
from app.models.base import utcnow
from app.repositories.order import InvoiceRepository
from app.repositories.reservation import ReservationRepository
from app.services.billing import BillingService
from app.services.pricing import late_fee_for


def sweep_overdue_reservations(session: Session, now: datetime | None = None) -> dict:
    """Flip picked-up reservations past their return window to OVERDUE."""

    now = now or utcnow()
    repo = ReservationRepository(session)
    affected = 0
    for reservation in repo.due_for_overdue_sweep(now):
        reservation.status = ReservationStatus.OVERDUE
        affected += 1
    session.flush()
    return {"swept": affected, "as_of": now.isoformat()}
