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


def current_user(
    authorization: str | None = Header(default=None),
    session: Session = Depends(db_session),
) -> User:
    token = _extract_bearer(authorization)
    return AuthService(session).resolve_session(token)


def require_role(minimum: Role) -> Callable[..., User]:
    """Build a dependency that enforces a minimum role rank."""

    def guard(user: User = Depends(current_user)) -> User:
        if _ROLE_RANK[user.role] < _ROLE_RANK[minimum]:
            raise PermissionDeniedError(
                f"this action requires the {minimum} role or higher"
            )
        return user

    return guard


require_viewer = require_role(Role.VIEWER)
require_agent = require_role(Role.AGENT)
require_manager = require_role(Role.MANAGER)
require_admin = require_role(Role.ADMIN)


def pagination(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=25, ge=1, le=100),
) -> PageParams:
    return PageParams(page=page, size=size)
