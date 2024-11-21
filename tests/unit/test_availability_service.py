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
