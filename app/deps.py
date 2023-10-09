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
