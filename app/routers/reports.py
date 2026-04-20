"""Dashboard and reporting endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import db_session, require_viewer
from app.models.base import utcnow
from app.models.user import User
from app.services.reports import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])
