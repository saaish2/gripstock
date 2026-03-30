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
