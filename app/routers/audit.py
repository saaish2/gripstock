"""Audit-log read endpoints (manager and above)."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.deps import db_session, require_manager
from app.models.user import User
from app.repositories.operations import AuditLogRepository
from app.schemas.common import ORMModel

router = APIRouter(prefix="/audit", tags=["audit"])


class AuditEntryOut(ORMModel):
