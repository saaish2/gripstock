"""Reservation endpoints, including availability checks."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.deps import db_session, pagination, require_agent
from app.enums import ReservationStatus
from app.models.user import User
from app.pagination import PageParams
from app.schemas.common import PagedResponse
from app.schemas.reservation import (
    AvailabilityQuery,
    AvailabilityResult,
    ReservationCreate,
    ReservationOut,
    ReservationReschedule,
)
from app.services.availability import AvailabilityService
from app.services.reservations import ReservationService

router = APIRouter(prefix="/reservations", tags=["reservations"])


@router.post("", response_model=ReservationOut, status_code=201)
def create_reservation(
    payload: ReservationCreate,
    actor: User = Depends(require_agent),
    session: Session = Depends(db_session),
) -> ReservationOut:
    data = payload.model_dump()
    reservation = ReservationService(session).create(data, actor_id=actor.id)
    return ReservationOut.model_validate(reservation)


@router.post("/availability", response_model=AvailabilityResult)
def availability(
    payload: AvailabilityQuery,
    _: User = Depends(require_agent),
    session: Session = Depends(db_session),
) -> AvailabilityResult:
    conflicts = ReservationService(session).check_availability(
        payload.asset_id, payload.starts_at, payload.ends_at
    )
    return AvailabilityResult(
        asset_id=payload.asset_id,
        available=not conflicts,
        conflicting_reservation_ids=conflicts,
    )


@router.get("/calendar/{asset_id}")
def asset_calendar(
    asset_id: int,
    starts_at: datetime,
    ends_at: datetime,
    _: User = Depends(require_agent),
    session: Session = Depends(db_session),
) -> dict:
    calendar = AvailabilityService(session).asset_calendar(asset_id, starts_at, ends_at)
    return calendar.to_dict()


@router.get("", response_model=PagedResponse[ReservationOut])
def list_reservations(
    customer_id: int | None = Query(default=None),
    status: ReservationStatus | None = Query(default=None),
    params: PageParams = Depends(pagination),
    _: User = Depends(require_agent),
    session: Session = Depends(db_session),
) -> dict:
    page = ReservationService(session).search(params, customer_id=customer_id, status=status)
    return page.to_dict(lambda r: ReservationOut.model_validate(r).model_dump())
