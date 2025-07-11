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

    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    late_fee_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    damage_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    tax_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    amount_paid: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))

    voided_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    payments: Mapped[list[Payment]] = relationship(
        back_populates="invoice", cascade="all, delete-orphan"
    )

    @property
    def balance_due(self) -> Decimal:
        return _d(self.total) - _d(self.amount_paid)

    @property
    def is_settled(self) -> bool:
        return self.balance_due <= _ZERO

    def recalculate_total(self) -> None:
        self.total = (
            _d(self.subtotal) + _d(self.late_fee_total) + _d(self.damage_total) + _d(self.tax_total)
        )


class Payment(Base, IntPrimaryKey, TimestampMixin):
    __tablename__ = "payments"

    invoice_id: Mapped[int] = mapped_column(
        ForeignKey("invoices.id", ondelete="CASCADE"), index=True, nullable=False
    )
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    method: Mapped[PaymentMethod] = mapped_column(String(20), nullable=False)
    reference: Mapped[str | None] = mapped_column(String(120), nullable=True)
    received_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    is_refund: Mapped[bool] = mapped_column(default=False, nullable=False)

    invoice: Mapped[Invoice] = relationship(back_populates="payments")
