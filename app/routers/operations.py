"""Checkout/checkin and maintenance endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.deps import db_session, require_agent, require_manager
from app.enums import MaintenanceStatus
from app.models.user import User
from app.repositories.operations import (
    DamageReportRepository,
    InspectionRepository,
    MaintenanceRepository,
)
from app.schemas.operations import (
    CheckinLine,
    CheckoutLine,
    DamageReportOut,
    InspectionOut,
    MaintenanceCreate,
    MaintenanceOut,
    MaintenanceUpdate,
)
from app.schemas.reservation import ReservationOut
from app.services.operations import CheckoutService, MaintenanceService

router = APIRouter(prefix="/operations", tags=["operations"])
