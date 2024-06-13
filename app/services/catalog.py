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
