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


@router.post("/reservations/{reservation_id}/checkin", response_model=ReservationOut)
def check_in(
    reservation_id: int,
    lines: list[CheckinLine],
    actor: User = Depends(require_agent),
    session: Session = Depends(db_session),
) -> ReservationOut:
    reservation, _damage = CheckoutService(session).check_in(
        reservation_id, [line.model_dump() for line in lines], actor_id=actor.id
    )
    return ReservationOut.model_validate(reservation)


@router.get("/reservations/{reservation_id}/inspections", response_model=list[InspectionOut])
def list_inspections(
    reservation_id: int,
    _: User = Depends(require_agent),
    session: Session = Depends(db_session),
) -> list[InspectionOut]:
    rows = InspectionRepository(session).for_reservation(reservation_id)
    return [InspectionOut.model_validate(r) for r in rows]


@router.get("/reservations/{reservation_id}/damage", response_model=list[DamageReportOut])
def list_damage(
    reservation_id: int,
    _: User = Depends(require_agent),
    session: Session = Depends(db_session),
) -> list[DamageReportOut]:
    rows = DamageReportRepository(session).for_reservation(reservation_id)
    return [DamageReportOut.model_validate(r) for r in rows]
