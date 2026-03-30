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
