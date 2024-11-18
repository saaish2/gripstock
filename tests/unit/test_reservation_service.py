"""Service tests for reservation availability and lifecycle."""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from app.enums import AssetStatus, ReservationStatus
from app.errors import ConflictError, InvalidStateError, ValidationError
from app.models.catalog import Asset, Category
from app.models.customer import Customer
from app.services.reservations import ReservationService


@pytest.fixture()
def fixtures(session):
    category = Category(name="Lighting", slug="lighting")
    session.add(category)
    session.flush()
    asset = Asset(
        category_id=category.id,
        name="Aputure 600d",
        barcode="LT-001",
        daily_rate=Decimal("85.00"),
        replacement_value=Decimal("1900.00"),
    )
    customer = Customer(name="Northwind", contact_email="a@b.com", credit_limit=Decimal("5000"))
    session.add_all([asset, customer])
    session.flush()
    return {"asset": asset, "customer": customer}


def _window(day_offset: int, length_days: int = 2):
    start = datetime(2024, 4, 1) + timedelta(days=day_offset)
    return start, start + timedelta(days=length_days)


def test_create_reservation_assigns_reference(session, fixtures):
    svc = ReservationService(session)
    start, end = _window(0)
    res = svc.create(
        {
            "customer_id": fixtures["customer"].id,
            "starts_at": start,
            "ends_at": end,
            "lines": [{"asset_id": fixtures["asset"].id}],
        }
    )
    assert res.reference.startswith("RSV-")
    assert res.status == ReservationStatus.PENDING


def test_overlapping_window_conflicts(session, fixtures):
    svc = ReservationService(session)
    start, end = _window(0, 3)
    data = {
        "customer_id": fixtures["customer"].id,
        "starts_at": start,
        "ends_at": end,
        "lines": [{"asset_id": fixtures["asset"].id}],
    }
    svc.create(data)

    overlap_start, overlap_end = _window(1, 3)
    with pytest.raises(ConflictError):
        svc.create(
            {
                "customer_id": fixtures["customer"].id,
                "starts_at": overlap_start,
                "ends_at": overlap_end,
                "lines": [{"asset_id": fixtures["asset"].id}],
            }
        )


def test_adjacent_window_is_allowed(session, fixtures):
    svc = ReservationService(session)
    start, end = _window(0, 2)  # apr1 - apr3
    svc.create(
        {
            "customer_id": fixtures["customer"].id,
            "starts_at": start,
            "ends_at": end,
            "lines": [{"asset_id": fixtures["asset"].id}],
        }
    )
    # Starts exactly when the first ends — half-open intervals don't overlap.
    res = svc.create(
        {
            "customer_id": fixtures["customer"].id,
            "starts_at": end,
            "ends_at": end + timedelta(days=2),
            "lines": [{"asset_id": fixtures["asset"].id}],
        }
    )
    assert res.status == ReservationStatus.PENDING


def test_cancelled_reservation_frees_inventory(session, fixtures):
    svc = ReservationService(session)
    start, end = _window(0, 3)
    res = svc.create(
        {
            "customer_id": fixtures["customer"].id,
            "starts_at": start,
            "ends_at": end,
            "lines": [{"asset_id": fixtures["asset"].id}],
        }
    )
    svc.confirm(res.id)
    svc.cancel(res.id)
    # Same window is now free.
    assert svc.is_available(fixtures["asset"].id, start, end)


def test_confirm_marks_asset_reserved(session, fixtures):
    svc = ReservationService(session)
    start, end = _window(0)
    res = svc.create(
        {
            "customer_id": fixtures["customer"].id,
            "starts_at": start,
            "ends_at": end,
            "lines": [{"asset_id": fixtures["asset"].id}],
        }
    )
    svc.confirm(res.id)
    session.refresh(fixtures["asset"])
    assert fixtures["asset"].status == AssetStatus.RESERVED


def test_cannot_return_directly_from_pending(session, fixtures):
    svc = ReservationService(session)
    start, end = _window(0)
    res = svc.create(
        {
            "customer_id": fixtures["customer"].id,
            "starts_at": start,
            "ends_at": end,
            "lines": [{"asset_id": fixtures["asset"].id}],
        }
    )
    with pytest.raises(InvalidStateError):
        svc.mark_no_show(res.id)  # only valid from confirmed
