"""Webhook subscription endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import db_session, require_admin
from app.models.user import User
from app.schemas.common import MessageResponse
from app.schemas.operations import WebhookCreate, WebhookOut
from app.services.webhooks import WebhookService

router = APIRouter(prefix="/webhooks", tags=["webhooks"])


@router.post("", response_model=WebhookOut, status_code=201)
def register_webhook(
    payload: WebhookCreate,
    _: User = Depends(require_admin),
    session: Session = Depends(db_session),
) -> WebhookOut:
    endpoint = WebhookService(session).register(payload.url, payload.secret, payload.event_types)
    return WebhookOut.model_validate(endpoint)


@router.get("", response_model=list[WebhookOut])
def list_webhooks(
    _: User = Depends(require_admin),
    session: Session = Depends(db_session),
) -> list[WebhookOut]:
    endpoints = WebhookService(session).endpoints.active_endpoints()
    return [WebhookOut.model_validate(e) for e in endpoints]


@router.delete("/{endpoint_id}", response_model=MessageResponse)
def deactivate_webhook(
    endpoint_id: int,
    _: User = Depends(require_admin),
    session: Session = Depends(db_session),
) -> MessageResponse:
    WebhookService(session).deactivate(endpoint_id)
    return MessageResponse(message="webhook deactivated")
