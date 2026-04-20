"""Dashboard and reporting endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import db_session, require_viewer
from app.models.base import utcnow
from app.models.user import User
from app.services.reports import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/dashboard")
def dashboard(
    _: User = Depends(require_viewer),
    session: Session = Depends(db_session),
) -> dict:
    return ReportService(session).dashboard(utcnow())


@router.get("/inventory")
def inventory(
    _: User = Depends(require_viewer),
    session: Session = Depends(db_session),
) -> dict:
    snapshot = ReportService(session).inventory_snapshot()
    return {
        "total": snapshot.total,
        "by_status": snapshot.by_status,
        "utilisation": snapshot.utilisation,
    }
