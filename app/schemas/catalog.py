"""Catalog schemas: categories, assets, kits."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.enums import AssetCondition, AssetStatus
from app.schemas.common import ORMModel


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=120)
    description: str | None = None
    parent_id: int | None = None


class CategoryOut(ORMModel):
    id: int
    name: str
    slug: str
    description: str | None = None
    parent_id: int | None = None


class AssetCreate(BaseModel):
    category_id: int
    name: str = Field(min_length=1, max_length=200)
    manufacturer: str | None = Field(default=None, max_length=120)
    model_number: str | None = Field(default=None, max_length=120)
    serial_number: str | None = Field(default=None, max_length=120)
    barcode: str = Field(min_length=1, max_length=64)
    condition: AssetCondition = AssetCondition.GOOD
    daily_rate: Decimal = Field(ge=0)
    weekly_rate: Decimal | None = Field(default=None, ge=0)
