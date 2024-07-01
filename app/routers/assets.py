"""Asset endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.deps import db_session, pagination, require_agent, require_manager
from app.enums import AssetStatus
from app.models.user import User
from app.pagination import PageParams
from app.schemas.catalog import (
    AssetCreate,
    AssetOut,
    AssetStatusUpdate,
    AssetUpdate,
)
from app.schemas.common import MessageResponse, PagedResponse
from app.services.catalog import AssetService

router = APIRouter(prefix="/assets", tags=["assets"])


@router.post("", response_model=AssetOut, status_code=201)
def create_asset(
    payload: AssetCreate,
    actor: User = Depends(require_manager),
    session: Session = Depends(db_session),
) -> AssetOut:
    asset = AssetService(session).create(payload.model_dump(), actor_id=actor.id)
    return AssetOut.model_validate(asset)


@router.get("", response_model=PagedResponse[AssetOut])
def list_assets(
    term: str | None = Query(default=None),
    category_id: int | None = Query(default=None),
    status: AssetStatus | None = Query(default=None),
    params: PageParams = Depends(pagination),
    _: User = Depends(require_agent),
    session: Session = Depends(db_session),
) -> dict:
    page = AssetService(session).search(params, term=term, category_id=category_id, status=status)
    return page.to_dict(lambda a: AssetOut.model_validate(a).model_dump())


@router.get("/{asset_id}", response_model=AssetOut)
def get_asset(
    asset_id: int,
    _: User = Depends(require_agent),
    session: Session = Depends(db_session),
) -> AssetOut:
    return AssetOut.model_validate(AssetService(session).get(asset_id))
