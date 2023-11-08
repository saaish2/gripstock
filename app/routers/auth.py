"""Authentication endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from app.deps import current_user, db_session
from app.models.user import User
from app.schemas.auth import (
    LoginRequest,
    LoginResponse,
    PasswordChange,
    UserOut,
)
from app.schemas.common import MessageResponse
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(
    payload: LoginRequest,
    user_agent: str | None = Header(default=None),
    session: Session = Depends(db_session),
) -> LoginResponse:
    service = AuthService(session)
    user, sess, token = service.authenticate(payload.email, payload.password, user_agent)
    return LoginResponse(token=token, expires_at=sess.expires_at, user=UserOut.model_validate(user))


@router.post("/logout", response_model=MessageResponse)
def logout(
    authorization: str = Header(),
    session: Session = Depends(db_session),
) -> MessageResponse:
    token = authorization.split(" ", 1)[-1]
    AuthService(session).logout(token)
    return MessageResponse(message="logged out")
