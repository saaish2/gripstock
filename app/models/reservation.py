"""Reservation and reservation-line ORM models."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.enums import ReservationStatus
from app.models.base import Base, IntPrimaryKey, TimestampMixin


class Reservation(Base, IntPrimaryKey, TimestampMixin):
    __tablename__ = "reservations"

    reference: Mapped[str] = mapped_column(String(20), unique=True, index=True, nullable=False)
    customer_id: Mapped[int] = mapped_column(
        ForeignKey("customers.id", ondelete="RESTRICT"), index=True, nullable=False
    )
