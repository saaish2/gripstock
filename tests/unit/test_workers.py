"""Tests for background sweeps and webhook dispatch."""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

import pytest

from app.enums import ReservationStatus, WebhookStatus
from app.models.base import utcnow
from app.models.catalog import Asset, Category
from app.models.customer import Customer
from app.services.reservations import ReservationService
from app.services.webhooks import WebhookService
from app.workers.sweeps import sweep_overdue_reservations
from app.workers.webhook_dispatcher import dispatch_due


@pytest.fixture()
def picked_up_reservation(session):
    category = Category(name="Grip", slug="grip")
    session.add(category)
    session.flush()
    asset = Asset(
        category_id=category.id,
        name="C-Stand",
        barcode="G-1",
        daily_rate=Decimal("12"),
        replacement_value=Decimal("260"),
    )
    customer = Customer(name="Cust", contact_email="c@d.com", credit_limit=Decimal("1000"))
    session.add_all([asset, customer])
    session.flush()

    svc = ReservationService(session)
    start = utcnow() - timedelta(days=5)
    res = svc.create(
        {
            "customer_id": customer.id,
            "starts_at": start,
            "ends_at": start + timedelta(days=2),
            "lines": [{"asset_id": asset.id}],
        }
    )
    res.status = ReservationStatus.PICKED_UP
    session.flush()
    return res
