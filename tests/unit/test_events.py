"""Tests for the domain-event dispatcher."""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal

from app.enums import WebhookStatus
from app.events import ALL_EVENTS, EventType, emit_event, envelope, is_known_event
from app.models.base import utcnow
from app.models.catalog import Asset, Category
from app.models.customer import Customer
from app.services.reservations import ReservationService
from app.services.webhooks import WebhookService


def test_known_events():
    assert is_known_event(EventType.RESERVATION_CREATED)
    assert not is_known_event("nope.invalid")
    assert len(ALL_EVENTS) >= 10


def test_envelope_shape():
    body = envelope(EventType.ORDER_CREATED, "order", 7, reference="ORD-1")
    assert body["event"] == "order.created"
    assert body["entity_type"] == "order"
    assert body["entity_id"] == "7"
    assert body["reference"] == "ORD-1"


def test_emit_creates_deliveries(session):
    WebhookService(session).register("https://x.example/h", "secret-val", ["*"])
    count = emit_event(session, EventType.INVOICE_PAID, envelope(EventType.INVOICE_PAID, "invoice", 1))
    assert count == 1


def test_reservation_create_emits_event(session):
    category = Category(name="Lighting", slug="lighting")
    session.add(category)
    session.flush()
    asset = Asset(
        category_id=category.id,
        name="Light",
        barcode="L-9",
        daily_rate=Decimal("50"),
        replacement_value=Decimal("900"),
    )
    customer = Customer(name="C", contact_email="c@e.com", credit_limit=Decimal("5000"))
    session.add_all([asset, customer])
    session.flush()

    WebhookService(session).register("https://x.example/h", "secret-val", ["reservation.created"])
    start = datetime(2025, 7, 1)
    ReservationService(session).create(
        {
            "customer_id": customer.id,
            "starts_at": start,
            "ends_at": start + timedelta(days=2),
            "lines": [{"asset_id": asset.id}],
        }
    )
    deliveries = WebhookService(session).deliveries.due(utcnow() + timedelta(minutes=1))
    assert any(d.event_type == "reservation.created" for d in deliveries)
    assert all(d.status == WebhookStatus.PENDING for d in deliveries)
