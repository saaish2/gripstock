"""Invoice and payment ORM models."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.enums import InvoiceStatus, PaymentMethod
from app.models.base import Base, IntPrimaryKey, TimestampMixin

_ZERO = Decimal("0.00")


def _d(value: Decimal | None) -> Decimal:
    """Coalesce a not-yet-flushed Numeric column to zero."""

    return value if value is not None else _ZERO
