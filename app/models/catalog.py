"""Catalog ORM models: categories, assets, kits, and kit membership."""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    Date,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.enums import AssetCondition, AssetStatus
from app.models.base import Base, IntPrimaryKey, SoftDeleteMixin, TimestampMixin


class Category(Base, IntPrimaryKey, TimestampMixin):
