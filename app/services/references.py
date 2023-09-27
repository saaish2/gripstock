"""Human-readable reference-number generation.

References are short, prefixed, zero-padded sequences derived from the row
count plus a base offset. They are deterministic given the table size, which
keeps tests predictable while still looking like real order numbers.
"""

from __future__ import annotations

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.billing import Invoice
from app.models.order import RentalOrder
from app.models.reservation import Reservation

RESERVATION_PREFIX = "RSV"
ORDER_PREFIX = "ORD"
INVOICE_PREFIX = "INV"

_BASE_OFFSET = 1000


def _next_sequence(session: Session, model) -> int:  # noqa: ANN001
    current = session.execute(select(func.count()).select_from(model)).scalar_one()
    return _BASE_OFFSET + current + 1
