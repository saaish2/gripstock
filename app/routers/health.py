"""Liveness and readiness endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.orm import Session

from app import __version__
from app.config import get_settings
from app.deps import db_session
from app.schemas.common import HealthResponse

router = APIRouter(tags=["health"])
