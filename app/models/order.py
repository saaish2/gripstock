"""Rental order and line-item ORM models."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.enums import OrderStatus
from app.models.base import Base, IntPrimaryKey, TimestampMixin


class RentalOrder(Base, IntPrimaryKey, TimestampMixin):
    __tablename__ = "rental_orders"

    reference: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    reservation_id: Mapped[int | None] = mapped_column(
        ForeignKey("reservations.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[OrderStatus] = mapped_column(
        String(20), default=OrderStatus.DRAFT, index=True, nullable=False
    )

    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    subtotal: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    discount_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    deposit_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    tax_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))
    grand_total: Mapped[Decimal] = mapped_column(Numeric(12, 2), default=Decimal("0.00"))

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    customer: Mapped[Customer] = relationship(back_populates="orders")  # noqa: F821
    lines: Mapped[list[OrderLine]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )

    def recalculate_totals(self) -> None:
        """Roll line subtotals/discounts/deposits up to the header."""

        self.subtotal = sum((line.line_subtotal for line in self.lines), Decimal("0.00"))
        self.discount_total = sum((line.discount_amount for line in self.lines), Decimal("0.00"))
        self.deposit_total = sum((line.deposit_amount for line in self.lines), Decimal("0.00"))
        net = self.subtotal - self.discount_total
        self.grand_total = net + self.tax_total


class OrderLine(Base, IntPrimaryKey):
