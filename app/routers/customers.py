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


@router.get("", response_model=PagedResponse[CustomerOut])
def list_customers(
    term: str | None = Query(default=None),
    status: CustomerStatus | None = Query(default=None),
    params: PageParams = Depends(pagination),
    _: User = Depends(require_agent),
    session: Session = Depends(db_session),
) -> dict:
    page = CustomerService(session).search(params, term=term, status=status)
    return page.to_dict(lambda c: CustomerOut.model_validate(c).model_dump())


@router.get("/{customer_id}", response_model=CustomerOut)
def get_customer(
    customer_id: int,
    _: User = Depends(require_agent),
    session: Session = Depends(db_session),
) -> CustomerOut:
    return CustomerOut.model_validate(CustomerService(session).get(customer_id))


@router.patch("/{customer_id}", response_model=CustomerOut)
def update_customer(
    customer_id: int,
    payload: CustomerUpdate,
    _: User = Depends(require_agent),
    session: Session = Depends(db_session),
) -> CustomerOut:
    customer = CustomerService(session).update(customer_id, payload.model_dump(exclude_unset=True))
    return CustomerOut.model_validate(customer)
