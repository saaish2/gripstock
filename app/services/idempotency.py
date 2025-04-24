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


def idempotent(
    session: Session,
    *,
    key: str | None,
    method: str,
    path: str,
    producer: Callable[[], T],
    response_code: int = 201,
) -> T | dict:
    """Run ``producer`` once per idempotency key, replaying the stored result."""

    if not key:
        return producer()

    repo = IdempotencyRepository(session)
    existing = repo.get_by_key(key)
    if existing is not None:
        if existing.method != method or existing.path != path:
            raise ConflictError(
                "idempotency key was already used for a different request"
            )
        return json.loads(existing.response_body)

    result = producer()
    body = result.model_dump() if isinstance(result, BaseModel) else result
    record = IdempotencyKey(
        key=key,
        method=method,
        path=path,
        response_code=response_code,
        response_body=json.dumps(body, default=str),
        created_at=utcnow(),
    )
    session.add(record)
    session.flush()
    return result
