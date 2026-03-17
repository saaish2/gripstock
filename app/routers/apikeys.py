"""API-key management endpoints (admin only)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import db_session, require_admin
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.operations import ApiKeyCreate, ApiKeyCreated, ApiKeyOut
from app.services.apikeys import ApiKeyService

router = APIRouter(prefix="/api-keys", tags=["api-keys"])


@router.post("", response_model=ApiKeyCreated, status_code=201)
def issue_key(
    payload: ApiKeyCreate,
    actor: User = Depends(require_admin),
    session: Session = Depends(db_session),
) -> ApiKeyCreated:
    key, plaintext = ApiKeyService(session).issue(payload.label, payload.scopes, created_by_id=actor.id)
    out = ApiKeyCreated.model_validate(key)
    out.plaintext_key = plaintext
    return out
