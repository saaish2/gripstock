"""Invoice and payment endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.deps import db_session, pagination, require_agent, require_manager
from app.enums import InvoiceStatus
from app.models.user import User
from app.pagination import PageParams
from app.repositories.order import PaymentRepository
from app.schemas.common import PagedResponse
from app.schemas.order import InvoiceOut, PaymentCreate, PaymentOut
from app.services.billing import BillingService
