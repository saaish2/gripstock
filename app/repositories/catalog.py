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

    def list_ordered(self) -> list[Category]:
        return list(self.session.execute(select(Category).order_by(Category.name)).scalars().all())

    def slug_taken(self, slug: str) -> bool:
        return self.get_by_slug(slug) is not None


class AssetRepository(BaseRepository[Asset]):
    model = Asset

    def active_query(self) -> Select:
        return select(Asset).where(Asset.deleted_at.is_(None))

    def get_by_barcode(self, barcode: str) -> Asset | None:
        stmt = self.active_query().where(Asset.barcode == barcode)
        return self.session.execute(stmt).scalar_one_or_none()

    def search_query(
        self,
        term: str | None = None,
        category_id: int | None = None,
        status: AssetStatus | None = None,
    ) -> Select:
        stmt = self.active_query()
        if term:
            like = f"%{term.lower()}%"
            stmt = stmt.where(
                or_(
                    Asset.name.ilike(like),
                    Asset.manufacturer.ilike(like),
                    Asset.serial_number.ilike(like),
                )
            )
        if category_id is not None:
            stmt = stmt.where(Asset.category_id == category_id)
        if status is not None:
            stmt = stmt.where(Asset.status == status)
        return stmt.order_by(Asset.name)

    def list_by_ids(self, asset_ids: list[int]) -> list[Asset]:
        if not asset_ids:
            return []
        stmt = self.active_query().where(Asset.id.in_(asset_ids))
        return list(self.session.execute(stmt).scalars().all())
