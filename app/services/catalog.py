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
