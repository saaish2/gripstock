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
