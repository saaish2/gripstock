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
    def __init__(self, session: Session) -> None:
        self.session = session
        self.users = UserRepository(session)
        self.sessions = SessionRepository(session)
        self.settings = get_settings()

    def create_user(
        self,
        *,
        email: str,
        full_name: str,
        password: str,
        role: Role = Role.AGENT,
        actor_id: int | None = None,
    ) -> User:
        email = email.lower().strip()
        if self.users.email_taken(email):
            raise ConflictError(f"a user with email {email!r} already exists")
        self._validate_password(password)
        user = User(
            email=email,
            full_name=full_name.strip(),
            password_hash=hash_password(password),
            role=role,
        )
        self.users.add(user)
        record_audit(
            self.session,
            actor_id=actor_id,
            action="user.created",
            entity_type="user",
            entity_id=user.id,
            payload={"email": email, "role": role},
        )
        return user
