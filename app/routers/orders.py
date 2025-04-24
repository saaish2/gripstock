"""Rental order endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Header, Query
from sqlalchemy.orm import Session

from app.deps import db_session, pagination, require_agent
from app.enums import OrderStatus
from app.models.user import User
from app.pagination import PageParams
from app.schemas.common import PagedResponse
from app.schemas.order import OrderFromReservation, OrderOut
from app.services.idempotency import idempotent
from app.services.orders import OrderService
