"""User-administration endpoints (admin only)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import db_session, require_admin
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.auth import UserCreate, UserOut, UserUpdate
from app.services.auth import AuthService

router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserOut, status_code=201)
def create_user(
    payload: UserCreate,
    actor: User = Depends(require_admin),
    session: Session = Depends(db_session),
) -> UserOut:
    user = AuthService(session).create_user(
        email=payload.email,
        full_name=payload.full_name,
        password=payload.password,
        role=payload.role,
        actor_id=actor.id,
    )
    return UserOut.model_validate(user)
