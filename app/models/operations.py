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
