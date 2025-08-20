"""Operational ORM models: inspections, damage reports, maintenance."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import Boolean, DateTime, ForeignKey, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.enums import AssetCondition, DamageSeverity, MaintenanceStatus
from app.models.base import Base, IntPrimaryKey, TimestampMixin


class Inspection(Base, IntPrimaryKey, TimestampMixin):
    __tablename__ = "inspections"

    reservation_id: Mapped[int] = mapped_column(
        ForeignKey("reservations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    asset_id: Mapped[int] = mapped_column(
        ForeignKey("assets.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    phase: Mapped[str] = mapped_column(String(12), nullable=False)  # checkout | checkin
    condition: Mapped[AssetCondition] = mapped_column(String(20), nullable=False)
    inspector_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    performed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)


class DamageReport(Base, IntPrimaryKey, TimestampMixin):
    __tablename__ = "damage_reports"

    asset_id: Mapped[int] = mapped_column(
        ForeignKey("assets.id", ondelete="RESTRICT"), index=True, nullable=False
    )
