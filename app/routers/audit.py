"""Audit-log read endpoints (manager and above)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.deps import db_session, require_manager
from app.models.user import User
from app.repositories.operations import AuditLogRepository
from app.schemas.common import ORMModel

router = APIRouter(prefix="/audit", tags=["audit"])


class AuditEntryOut(ORMModel):
    id: int
    actor_id: int | None = None
    action: str
    entity_type: str
    entity_id: str
    payload: str | None = None


@router.get("", response_model=list[AuditEntryOut])
def recent(
    limit: int = Query(default=100, ge=1, le=500),
    _: User = Depends(require_manager),
    session: Session = Depends(db_session),
) -> list[AuditEntryOut]:
    rows = AuditLogRepository(session).recent(limit)
    return [AuditEntryOut.model_validate(r) for r in rows]


@router.get("/{entity_type}/{entity_id}", response_model=list[AuditEntryOut])
def for_entity(
    entity_type: str,
    entity_id: str,
    _: User = Depends(require_manager),
    session: Session = Depends(db_session),
) -> list[AuditEntryOut]:
    rows = AuditLogRepository(session).for_entity(entity_type, entity_id)
    return [AuditEntryOut.model_validate(r) for r in rows]
