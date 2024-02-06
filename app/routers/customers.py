"""Customer endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.deps import db_session, pagination, require_agent, require_manager
from app.enums import CustomerStatus
from app.models.user import User
from app.pagination import PageParams
from app.schemas.common import MessageResponse, PagedResponse
from app.schemas.customer import (
    CustomerCreate,
    CustomerOut,
    CustomerStatusUpdate,
    CustomerUpdate,
)
from app.services.customers import CustomerService
