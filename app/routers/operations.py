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
maintenance_router = APIRouter(prefix="/maintenance", tags=["maintenance"])


@router.post("/reservations/{reservation_id}/checkout", response_model=ReservationOut)
def check_out(
    reservation_id: int,
    lines: list[CheckoutLine],
    actor: User = Depends(require_agent),
    session: Session = Depends(db_session),
) -> ReservationOut:
    reservation = CheckoutService(session).check_out(
        reservation_id, [line.model_dump() for line in lines], actor_id=actor.id
    )
    return ReservationOut.model_validate(reservation)
