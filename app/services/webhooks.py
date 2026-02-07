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
