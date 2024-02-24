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
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
    slug: Mapped[str] = mapped_column(String(140), unique=True, index=True, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id", ondelete="SET NULL"), nullable=True
    )

    assets: Mapped[list[Asset]] = relationship(back_populates="category")
    children: Mapped[list[Category]] = relationship()
