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


def _asset(session, category_id, barcode="A-1") -> int:
    return AssetService(session).create(
        {
            "category_id": category_id,
            "name": "Body",
            "barcode": barcode,
            "daily_rate": Decimal("100"),
            "replacement_value": Decimal("1000"),
        }
    ).id


def test_duplicate_barcode_rejected(session):
    cat = _category(session)
    _asset(session, cat, "DUP")
    with pytest.raises(ConflictError):
        _asset(session, cat, "DUP")


def test_asset_status_transition(session):
    cat = _category(session)
    aid = _asset(session, cat)
    svc = AssetService(session)
    svc.change_status(aid, AssetStatus.IN_MAINTENANCE)
    assert svc.get(aid).status == AssetStatus.IN_MAINTENANCE


def test_illegal_asset_transition(session):
    cat = _category(session)
    aid = _asset(session, cat)
    svc = AssetService(session)
    svc.change_status(aid, AssetStatus.RETIRED)
    with pytest.raises(InvalidStateError):
        svc.change_status(aid, AssetStatus.AVAILABLE)


def test_kit_requires_existing_assets(session):
    with pytest.raises(NotFoundError):
        KitService(session).create("Bundle", [{"asset_id": 999}])
