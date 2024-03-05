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


class Asset(Base, IntPrimaryKey, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "assets"
    __table_args__ = (UniqueConstraint("barcode", name="uq_asset_barcode"),)

    category_id: Mapped[int] = mapped_column(
        ForeignKey("categories.id", ondelete="RESTRICT"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(200), index=True, nullable=False)
    manufacturer: Mapped[str | None] = mapped_column(String(120), nullable=True)
    model_number: Mapped[str | None] = mapped_column(String(120), nullable=True)
    serial_number: Mapped[str | None] = mapped_column(String(120), index=True, nullable=True)
    barcode: Mapped[str] = mapped_column(String(64), index=True, nullable=False)

    status: Mapped[AssetStatus] = mapped_column(
        String(20), default=AssetStatus.AVAILABLE, index=True, nullable=False
    )
    condition: Mapped[AssetCondition] = mapped_column(
        String(20), default=AssetCondition.GOOD, nullable=False
    )
