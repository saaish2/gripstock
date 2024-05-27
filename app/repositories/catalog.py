"""Catalog repositories: categories, assets, kits."""

from __future__ import annotations

from sqlalchemy import Select, or_, select

from app.enums import AssetStatus
from app.models.catalog import Asset, Category, Kit, KitItem
from app.repositories.base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    model = Category

    def get_by_slug(self, slug: str) -> Category | None:
        stmt = select(Category).where(Category.slug == slug)
        return self.session.execute(stmt).scalar_one_or_none()
