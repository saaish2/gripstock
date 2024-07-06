"""Kit (bundle) endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import db_session, require_agent, require_manager
from app.models.user import User
from app.schemas.catalog import KitCreate, KitOut
from app.schemas.common import MessageResponse
from app.services.catalog import KitService

router = APIRouter(prefix="/kits", tags=["kits"])


@router.post("", response_model=KitOut, status_code=201)
def create_kit(
    payload: KitCreate,
    _: User = Depends(require_manager),
    session: Session = Depends(db_session),
) -> KitOut:
    kit = KitService(session).create(
        payload.name,
        [item.model_dump() for item in payload.items],
        description=payload.description,
        bundle_discount_rate=payload.bundle_discount_rate,
    )
    return KitOut.model_validate(kit)


@router.get("", response_model=list[KitOut])
def list_kits(
    _: User = Depends(require_agent),
    session: Session = Depends(db_session),
) -> list[KitOut]:
    return [KitOut.model_validate(k) for k in KitService(session).list_active()]


@router.get("/{kit_id}", response_model=KitOut)
def get_kit(
    kit_id: int,
    _: User = Depends(require_agent),
    session: Session = Depends(db_session),
) -> KitOut:
    return KitOut.model_validate(KitService(session).get(kit_id))


@router.delete("/{kit_id}", response_model=MessageResponse)
def deactivate_kit(
    kit_id: int,
    _: User = Depends(require_manager),
    session: Session = Depends(db_session),
) -> MessageResponse:
    KitService(session).deactivate(kit_id)
    return MessageResponse(message="kit deactivated")
