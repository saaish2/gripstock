"""Idempotency helper for unsafe POST endpoints.

When a client supplies an ``Idempotency-Key`` header, the first successful
response is persisted and replayed verbatim for any later request carrying the
same key. This makes order creation safe to retry after a network blip without
double-booking inventory.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import TypeVar

from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.errors import ConflictError
from app.models.base import utcnow
from app.models.platform import IdempotencyKey
from app.repositories.operations import IdempotencyRepository

T = TypeVar("T", bound=BaseModel)
