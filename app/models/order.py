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
