"""Service tests for catalog: assets, status transitions, kits."""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.enums import AssetStatus
from app.errors import ConflictError, InvalidStateError, NotFoundError
from app.services.catalog import AssetService, CategoryService, KitService, slugify


def test_slugify():
    assert slugify("Cinema Cameras") == "cinema-cameras"
    assert slugify("LED / HMI") == "led-hmi"


def _category(session) -> int:
    return CategoryService(session).create("Cameras").id
