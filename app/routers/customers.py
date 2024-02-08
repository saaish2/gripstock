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

router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("", response_model=CustomerOut, status_code=201)
def create_customer(
    payload: CustomerCreate,
    actor: User = Depends(require_agent),
    session: Session = Depends(db_session),
) -> CustomerOut:
    customer = CustomerService(session).create(payload.model_dump(), actor_id=actor.id)
    return CustomerOut.model_validate(customer)
