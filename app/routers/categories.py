"""Category endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import db_session, require_agent, require_manager
from app.models.user import User
from app.schemas.catalog import CategoryCreate, CategoryOut
from app.services.catalog import CategoryService

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("", response_model=CategoryOut, status_code=201)
def create_category(
    payload: CategoryCreate,
    _: User = Depends(require_manager),
    session: Session = Depends(db_session),
) -> CategoryOut:
    category = CategoryService(session).create(
        payload.name, description=payload.description, parent_id=payload.parent_id
    )
    return CategoryOut.model_validate(category)
