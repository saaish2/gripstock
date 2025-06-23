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


class Invoice(Base, IntPrimaryKey, TimestampMixin):
    __tablename__ = "invoices"

    number: Mapped[str] = mapped_column(String(24), unique=True, index=True, nullable=False)
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    order_id: Mapped[int | None] = mapped_column(
        ForeignKey("rental_orders.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[InvoiceStatus] = mapped_column(
        String(20), default=InvoiceStatus.DRAFT, index=True, nullable=False
    )

    issued_on: Mapped[date | None] = mapped_column(Date, nullable=True)
    due_on: Mapped[date | None] = mapped_column(Date, nullable=True)
