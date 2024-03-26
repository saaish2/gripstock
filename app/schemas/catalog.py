"""Catalog schemas: categories, assets, kits."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.enums import AssetCondition, AssetStatus
from app.schemas.common import ORMModel


class CategoryCreate(BaseModel):
