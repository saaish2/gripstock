"""Catalog service: categories, assets, kits, and status transitions."""

from __future__ import annotations

import re

from sqlalchemy.orm import Session

from app.enums import ASSET_TRANSITIONS, AssetStatus, can_transition
from app.errors import ConflictError, InvalidStateError, NotFoundError, ValidationError
from app.models.base import utcnow
from app.models.catalog import Asset, Category, Kit, KitItem
from app.pagination import Page, PageParams, paginate
from app.repositories.catalog import AssetRepository, CategoryRepository, KitRepository
from app.services.audit import record_audit

_SLUG_RE = re.compile(r"[^a-z0-9]+")


def slugify(value: str) -> str:
    slug = _SLUG_RE.sub("-", value.lower()).strip("-")
    if not slug:
        raise ValidationError("cannot derive a slug from an empty name")
    return slug


class CategoryService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = CategoryRepository(session)

    def create(self, name: str, description: str | None = None, parent_id: int | None = None) -> Category:
        slug = slugify(name)
        if self.repo.slug_taken(slug):
            raise ConflictError(f"a category with slug {slug!r} already exists")
        if parent_id is not None and self.repo.get(parent_id) is None:
            raise NotFoundError(f"parent category {parent_id} not found")
        category = Category(name=name.strip(), slug=slug, description=description, parent_id=parent_id)
        self.repo.add(category)
        return category

    def get(self, category_id: int) -> Category:
        category = self.repo.get(category_id)
        if category is None:
            raise NotFoundError(f"category {category_id} not found")
        return category

    def list(self) -> list[Category]:
        return self.repo.list_ordered()


class AssetService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = AssetRepository(session)
        self.categories = CategoryRepository(session)

    def create(self, data: dict, actor_id: int | None = None) -> Asset:
        if self.categories.get(data["category_id"]) is None:
            raise NotFoundError(f"category {data['category_id']} not found")
        if self.repo.barcode_taken(data["barcode"]):
            raise ConflictError(f"barcode {data['barcode']!r} is already in use")
        asset = Asset(**data)
        self.repo.add(asset)
        record_audit(
            self.session,
            actor_id=actor_id,
            action="asset.created",
            entity_type="asset",
            entity_id=asset.id,
        )
        return asset

    def get(self, asset_id: int) -> Asset:
        asset = self.repo.get(asset_id)
        if asset is None or asset.deleted_at is not None:
            raise NotFoundError(f"asset {asset_id} not found")
        return asset

    def update(self, asset_id: int, changes: dict) -> Asset:
        asset = self.get(asset_id)
        for field, value in changes.items():
            if value is not None:
                setattr(asset, field, value)
        self.session.flush()
        return asset

    def change_status(self, asset_id: int, target: AssetStatus, actor_id: int | None = None) -> Asset:
        asset = self.get(asset_id)
        if target == asset.status:
            return asset
        if not can_transition(ASSET_TRANSITIONS, asset.status, target):
            raise InvalidStateError(f"cannot move asset from {asset.status} to {target}")
        previous = asset.status
        asset.status = target
        self.session.flush()
        record_audit(
            self.session,
            actor_id=actor_id,
            action="asset.status_changed",
            entity_type="asset",
            entity_id=asset.id,
            payload={"from": previous, "to": target},
        )
        return asset

    def retire(self, asset_id: int) -> Asset:
        return self.change_status(asset_id, AssetStatus.RETIRED)

    def soft_delete(self, asset_id: int) -> None:
        asset = self.get(asset_id)
        if asset.status in (AssetStatus.RESERVED, AssetStatus.CHECKED_OUT):
            raise InvalidStateError("cannot delete an asset that is reserved or checked out")
        asset.deleted_at = utcnow()
        self.session.flush()

    def search(
        self,
        params: PageParams,
        term: str | None = None,
        category_id: int | None = None,
        status: AssetStatus | None = None,
    ) -> Page:
        stmt = self.repo.search_query(term, category_id, status)
        return paginate(self.session, stmt, params)


class KitService:
