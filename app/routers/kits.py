"""Kit (bundle) endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import db_session, require_agent, require_manager
from app.models.user import User
from app.schemas.catalog import KitCreate, KitOut
from app.schemas.common import MessageResponse
from app.services.catalog import KitService
