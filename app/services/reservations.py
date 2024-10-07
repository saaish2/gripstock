"""Reservation service: availability, lifecycle, and inventory holds."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy.orm import Session

from app.enums import (
    RESERVATION_TRANSITIONS,
    AssetStatus,
    CustomerStatus,
    ReservationStatus,
    can_transition,
)
from app.errors import (
    BusinessRuleError,
    ConflictError,
    InvalidStateError,
    NotFoundError,
    ValidationError,
)
from app.events import EventType, emit_event, envelope
from app.models.reservation import Reservation, ReservationLine
from app.pagination import Page, PageParams, paginate
from app.repositories.catalog import AssetRepository
from app.repositories.customer import CustomerRepository
from app.repositories.reservation import ReservationRepository
from app.services.audit import record_audit
from app.services.references import next_reservation_reference
