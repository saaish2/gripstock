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


ALL_EVENTS: tuple[str, ...] = (
    EventType.RESERVATION_CREATED,
    EventType.RESERVATION_CONFIRMED,
    EventType.RESERVATION_CANCELLED,
    EventType.RESERVATION_CHECKED_OUT,
    EventType.RESERVATION_CHECKED_IN,
    EventType.ORDER_CREATED,
    EventType.INVOICE_ISSUED,
    EventType.INVOICE_PAID,
    EventType.PAYMENT_RECEIVED,
    EventType.ASSET_RETIRED,
    EventType.DAMAGE_REPORTED,
)


def is_known_event(event_type: str) -> bool:
    return event_type in ALL_EVENTS
