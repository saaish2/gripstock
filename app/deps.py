"""FastAPI dependencies: database sessions, auth, and RBAC guards."""

from __future__ import annotations

from collections.abc import Callable, Iterator

from fastapi import Depends, Header, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.enums import Role
from app.errors import AuthenticationError, PermissionDeniedError
from app.models.user import User
from app.pagination import PageParams
from app.services.auth import AuthService

# Role hierarchy — higher numbers strictly include the powers of lower ones.
_ROLE_RANK: dict[Role, int] = {
    Role.VIEWER: 0,
    Role.AGENT: 1,
    Role.MANAGER: 2,
    Role.ADMIN: 3,
}


def db_session() -> Iterator[Session]:
    yield from get_db()


def _extract_bearer(authorization: str | None) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise AuthenticationError("missing or malformed Authorization header")
    return authorization.split(" ", 1)[1].strip()
