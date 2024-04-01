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
