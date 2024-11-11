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
