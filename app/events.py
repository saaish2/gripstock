"""Domain-event constants and a thin dispatcher.

Services describe what happened in terms of stable event names; the dispatcher
turns those into webhook deliveries. Keeping the catalogue in one place means
the webhook subscription UI and the docs can enumerate exactly what a customer
can listen for.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy.orm import Session

from app.logging import get_logger, log_event
from app.services.webhooks import WebhookService

logger = get_logger("events")


class EventType:
    RESERVATION_CREATED = "reservation.created"
    RESERVATION_CONFIRMED = "reservation.confirmed"
    RESERVATION_CANCELLED = "reservation.cancelled"
    RESERVATION_CHECKED_OUT = "reservation.checked_out"
    RESERVATION_CHECKED_IN = "reservation.checked_in"
    ORDER_CREATED = "order.created"
    INVOICE_ISSUED = "invoice.issued"
    INVOICE_PAID = "invoice.paid"
    PAYMENT_RECEIVED = "payment.received"
    ASSET_RETIRED = "asset.retired"
    DAMAGE_REPORTED = "damage.reported"
