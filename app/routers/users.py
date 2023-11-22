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


@router.get("", response_model=list[UserOut])
def list_users(
    _: User = Depends(require_admin),
    session: Session = Depends(db_session),
) -> list[UserOut]:
    users = UserRepository(session).list_active()
    return [UserOut.model_validate(u) for u in users]


@router.patch("/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    payload: UserUpdate,
    _: User = Depends(require_admin),
    session: Session = Depends(db_session),
) -> UserOut:
    user = AuthService(session).update_user(
        user_id,
        full_name=payload.full_name,
        role=payload.role,
        is_active=payload.is_active,
    )
    return UserOut.model_validate(user)
