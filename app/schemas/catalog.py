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
    monthly_rate: Decimal | None = Field(default=None, ge=0)
    replacement_value: Decimal = Field(ge=0)
    acquired_on: date | None = None
    home_location: str | None = Field(default=None, max_length=120)
    notes: str | None = None


class AssetUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=200)
    condition: AssetCondition | None = None
    daily_rate: Decimal | None = Field(default=None, ge=0)
    weekly_rate: Decimal | None = Field(default=None, ge=0)
    monthly_rate: Decimal | None = Field(default=None, ge=0)
    replacement_value: Decimal | None = Field(default=None, ge=0)
    home_location: str | None = Field(default=None, max_length=120)
    notes: str | None = None


class AssetStatusUpdate(BaseModel):
    status: AssetStatus


class AssetOut(ORMModel):
    id: int
    category_id: int
    name: str
    manufacturer: str | None = None
    model_number: str | None = None
    serial_number: str | None = None
    barcode: str
    status: AssetStatus
    condition: AssetCondition
    daily_rate: Decimal
    weekly_rate: Decimal | None = None
    monthly_rate: Decimal | None = None
    replacement_value: Decimal
    home_location: str | None = None
    created_at: datetime


class KitItemIn(BaseModel):
    asset_id: int
    quantity: int = Field(default=1, ge=1)


class KitCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    description: str | None = None
    bundle_discount_rate: Decimal = Field(default=Decimal("0.0000"), ge=0, le=1)
    items: list[KitItemIn] = Field(default_factory=list)


class KitItemOut(ORMModel):
