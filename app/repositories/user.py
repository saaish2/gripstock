"""User and session repositories."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select

from app.models.user import Session as SessionModel
from app.models.user import User
from app.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email.lower())
        return self.session.execute(stmt).scalar_one_or_none()

    def list_active(self) -> list[User]:
        stmt = select(User).where(User.is_active.is_(True)).order_by(User.full_name)
        return list(self.session.execute(stmt).scalars().all())

    def email_taken(self, email: str) -> bool:
        return self.get_by_email(email) is not None


class SessionRepository(BaseRepository[SessionModel]):
    model = SessionModel
