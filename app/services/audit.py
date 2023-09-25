"""Audit-log helper used by every mutating service."""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.base import utcnow
from app.models.platform import AuditLog


def record_audit(
    session: Session,
    *,
    actor_id: int | None,
    action: str,
    entity_type: str,
    entity_id: Any,
    payload: dict[str, Any] | None = None,
) -> AuditLog:
    """Append an immutable audit entry within the caller's transaction."""

    entry = AuditLog(
        actor_id=actor_id,
        action=action,
        entity_type=entity_type,
        entity_id=str(entity_id),
        payload=json.dumps(payload, default=str) if payload else None,
        created_at=utcnow(),
    )
    session.add(entry)
    session.flush()
    return entry
