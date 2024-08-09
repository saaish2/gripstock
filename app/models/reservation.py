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
    created_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    status: Mapped[ReservationStatus] = mapped_column(
        String(20), default=ReservationStatus.PENDING, index=True, nullable=False
    )

    starts_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    ends_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True, nullable=False)
    picked_up_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    returned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    customer: Mapped[Customer] = relationship(back_populates="reservations")  # noqa: F821
    lines: Mapped[list[ReservationLine]] = relationship(
        back_populates="reservation", cascade="all, delete-orphan"
    )

    @property
    def is_open(self) -> bool:
        return self.status in (
            ReservationStatus.PENDING,
            ReservationStatus.CONFIRMED,
            ReservationStatus.PICKED_UP,
            ReservationStatus.OVERDUE,
        )

    @property
    def rental_days(self) -> int:
        delta = self.ends_at - self.starts_at
        return max(1, -(-delta.days if delta.days else 1))


class ReservationLine(Base, IntPrimaryKey):
