"""Service tests for the availability calendar."""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from app.errors import NotFoundError, ValidationError
from app.models.catalog import Asset, Category
from app.models.customer import Customer
from app.services.availability import AvailabilityService
from app.services.reservations import ReservationService


@pytest.fixture()
def booked(session):
    category = Category(name="Audio", slug="audio")
    session.add(category)
    session.flush()
    asset = Asset(
        category_id=category.id,
        name="MixPre",
        barcode="AU-1",
        daily_rate=Decimal("70"),
        replacement_value=Decimal("1200"),
    )
    customer = Customer(name="C", contact_email="c@x.com", credit_limit=Decimal("9000"))
    session.add_all([asset, customer])
    session.flush()

    start = datetime(2025, 6, 1)
    ReservationService(session).create(
        {
            "customer_id": customer.id,
            "starts_at": start,
            "ends_at": start + timedelta(days=3),
            "lines": [{"asset_id": asset.id}],
        }
    )
    return {"asset": asset, "start": start}


def test_calendar_shows_booked_interval(session, booked):
    svc = AvailabilityService(session)
    cal = svc.asset_calendar(
        booked["asset"].id,
        booked["start"] - timedelta(days=2),
        booked["start"] + timedelta(days=10),
    )
    assert not cal.is_free
    assert len(cal.intervals) == 1


def test_calendar_free_outside_window(session, booked):
    svc = AvailabilityService(session)
    later = booked["start"] + timedelta(days=20)
    cal = svc.asset_calendar(booked["asset"].id, later, later + timedelta(days=2))
    assert cal.is_free


def test_free_assets_filters(session, booked):
    svc = AvailabilityService(session)
    free = svc.free_assets(
        [booked["asset"].id], booked["start"], booked["start"] + timedelta(days=1)
    )
    assert free == []


def test_calendar_unknown_asset(session):
    with pytest.raises(NotFoundError):
        AvailabilityService(session).asset_calendar(999, datetime(2025, 1, 1), datetime(2025, 1, 2))


def test_calendar_bad_window(session, booked):
    with pytest.raises(ValidationError):
        AvailabilityService(session).asset_calendar(
            booked["asset"].id, booked["start"], booked["start"]
        )
