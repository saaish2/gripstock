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
