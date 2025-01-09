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
