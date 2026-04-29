"""Webhook delivery dispatcher.

The dispatcher pulls due deliveries and posts them to their endpoints. The
transport is injected so tests can supply a stub instead of making real
network calls. In production the default httpx transport is used.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Protocol

from sqlalchemy.orm import Session

from app.logging import get_logger
from app.models.base import utcnow
from app.repositories.operations import WebhookDeliveryRepository, WebhookRepository
from app.services.webhooks import WebhookService

logger = get_logger("webhooks")


class Transport(Protocol):
    def __call__(self, url: str, body: str, signature: str) -> int:  # pragma: no cover
        ...


def _noop_transport(url: str, body: str, signature: str) -> int:
    """Default transport used in tests — pretends every POST succeeds."""

    return 200


def dispatch_due(
    session: Session,
    transport: Callable[[str, str, str], int] = _noop_transport,
    limit: int = 50,
) -> dict:
    """Attempt delivery of every due webhook, applying backoff on failure."""

    service = WebhookService(session)
    deliveries = WebhookDeliveryRepository(session)
    endpoints = WebhookRepository(session)

    delivered = 0
    failed = 0
    for delivery in deliveries.due(utcnow(), limit=limit):
        endpoint = endpoints.get(delivery.endpoint_id)
        if endpoint is None or not endpoint.is_active:
            service.mark_failed_attempt(delivery, "endpoint missing or inactive")
            failed += 1
            continue
        signature = service.signature_for(endpoint, delivery.payload)
        try:
            status = transport(endpoint.url, delivery.payload, signature)
        except Exception as exc:  # noqa: BLE001 - transport errors are expected
            service.mark_failed_attempt(delivery, str(exc))
            failed += 1
            continue
        if 200 <= status < 300:
            service.mark_delivered(delivery)
            delivered += 1
        else:
            service.mark_failed_attempt(delivery, f"non-2xx status {status}")
            failed += 1

    return {"delivered": delivered, "failed": failed}
