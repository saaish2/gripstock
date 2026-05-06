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
