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
