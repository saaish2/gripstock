"""User-administration endpoints (admin only)."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import db_session, require_admin
from app.models.user import User
from app.repositories.user import UserRepository
from app.schemas.auth import UserCreate, UserOut, UserUpdate
from app.services.auth import AuthService
