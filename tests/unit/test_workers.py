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


def test_overdue_sweep_flips_status(session, picked_up_reservation):
    result = sweep_overdue_reservations(session, utcnow())
    assert result["swept"] == 1
    session.refresh(picked_up_reservation)
    assert picked_up_reservation.status == ReservationStatus.OVERDUE


def test_webhook_emit_and_dispatch(session):
    svc = WebhookService(session)
    svc.register("https://example.test/hook", "secret-value", ["reservation.created"])
    deliveries = svc.emit("reservation.created", {"id": 1})
    assert len(deliveries) == 1

    result = dispatch_due(session, transport=lambda url, body, sig: 200)
    assert result["delivered"] == 1
    session.refresh(deliveries[0])
    assert deliveries[0].status == WebhookStatus.DELIVERED
