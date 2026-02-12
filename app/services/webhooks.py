"""Webhook subscription and delivery service.

Deliveries are persisted as rows and dispatched by a background worker. The
service computes exponential backoff and flips a delivery to ``FAILED`` once
the configured attempt ceiling is reached.
"""

from __future__ import annotations

import hashlib
import hmac
import json
from datetime import timedelta

from sqlalchemy.orm import Session

from app.config import get_settings
from app.enums import WebhookStatus
from app.errors import NotFoundError
from app.models.base import utcnow
from app.models.platform import WebhookDelivery, WebhookEndpoint
from app.repositories.operations import WebhookDeliveryRepository, WebhookRepository


def sign_payload(secret: str, body: str) -> str:
    """Return the hex HMAC-SHA256 signature for a webhook body."""

    return hmac.new(secret.encode(), body.encode(), hashlib.sha256).hexdigest()


class WebhookService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.settings = get_settings()
        self.endpoints = WebhookRepository(session)
        self.deliveries = WebhookDeliveryRepository(session)

    def register(self, url: str, secret: str, event_types: list[str]) -> WebhookEndpoint:
        endpoint = WebhookEndpoint(
            url=url,
            secret=secret,
            event_types=",".join(event_types) if event_types else "*",
        )
        self.endpoints.add(endpoint)
        return endpoint

    def get(self, endpoint_id: int) -> WebhookEndpoint:
        endpoint = self.endpoints.get(endpoint_id)
        if endpoint is None:
            raise NotFoundError(f"webhook endpoint {endpoint_id} not found")
        return endpoint

    def deactivate(self, endpoint_id: int) -> WebhookEndpoint:
        endpoint = self.get(endpoint_id)
        endpoint.is_active = False
        self.session.flush()
        return endpoint
