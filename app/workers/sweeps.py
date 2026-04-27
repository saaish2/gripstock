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


def sweep_invoice_late_fees(session: Session, now: datetime | None = None) -> dict:
    """Accrue late fees on every overdue invoice and mark them OVERDUE."""

    now = now or utcnow()
    today = now.date()
    billing = BillingService(session)
    invoices = InvoiceRepository(session)

    accrued_total = 0
    for invoice in invoices.overdue_as_of(today):
        days_late = (today - invoice.due_on).days if invoice.due_on else 0
        if days_late <= 0:
            continue
        daily = invoice.subtotal / max(1, days_late)
        fee = late_fee_for(daily, 1, billing.settings)
        if fee > 0:
            billing.accrue_late_fee(invoice.id, daily, 1)
            accrued_total += 1
    return {"invoices_touched": accrued_total, "as_of": today.isoformat()}


def run_all(session: Session, now: datetime | None = None) -> dict:
    now = now or utcnow()
    return {
        "reservations": sweep_overdue_reservations(session, now),
        "late_fees": sweep_invoice_late_fees(session, now),
    }
