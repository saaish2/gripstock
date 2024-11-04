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
