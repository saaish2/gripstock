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

    def authenticate(
        self, email: str, password: str, user_agent: str | None = None
    ) -> tuple[User, SessionModel, str]:
        user = self.users.get_by_email(email.lower().strip())
        if user is None or not verify_password(password, user.password_hash):
            raise AuthenticationError("invalid email or password")
        if not user.is_active:
            raise AuthenticationError("this account is disabled")

        now = utcnow()
        user.last_login_at = now
        token = generate_token()
        session = SessionModel(
            user_id=user.id,
            token_fingerprint=fingerprint_token(token),
            expires_at=now + timedelta(minutes=self.settings.session_ttl_minutes),
            user_agent=user_agent,
        )
        self.sessions.add(session)
        return user, session, token

    def resolve_session(self, token: str) -> User:
        fingerprint = fingerprint_token(token)
        session = self.sessions.get_by_fingerprint(fingerprint)
        now = utcnow()
        if session is None or session.revoked_at is not None or session.expires_at <= now:
            raise AuthenticationError("session is invalid or has expired")
        user = self.users.get(session.user_id)
        if user is None or not user.is_active:
            raise AuthenticationError("user is no longer active")
        return user

    def logout(self, token: str) -> None:
        session = self.sessions.get_by_fingerprint(fingerprint_token(token))
        if session is not None and session.revoked_at is None:
            session.revoked_at = utcnow()
            self.session.flush()
