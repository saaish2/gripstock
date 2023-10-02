"""Authentication and user-management service."""

from __future__ import annotations

from datetime import timedelta

from sqlalchemy.orm import Session

from app.config import get_settings
from app.enums import Role
from app.errors import (
    AuthenticationError,
    ConflictError,
    NotFoundError,
    ValidationError,
)
from app.models.base import utcnow
from app.models.user import Session as SessionModel
from app.models.user import User
from app.repositories.user import SessionRepository, UserRepository
from app.security import (
    fingerprint_token,
    generate_token,
    hash_password,
    verify_password,
)
from app.services.audit import record_audit


class AuthService:
