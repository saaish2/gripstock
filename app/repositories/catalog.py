"""Catalog repositories: categories, assets, kits."""

from __future__ import annotations

from sqlalchemy import Select, or_, select

from app.enums import AssetStatus
from app.models.catalog import Asset, Category, Kit, KitItem
from app.repositories.base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
