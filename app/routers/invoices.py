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

router = APIRouter(prefix="/invoices", tags=["invoices"])


@router.post("/from-order/{order_id}", response_model=InvoiceOut, status_code=201)
def create_invoice(
    order_id: int,
    actor: User = Depends(require_agent),
    session: Session = Depends(db_session),
) -> InvoiceOut:
    invoice = BillingService(session).create_for_order(order_id, actor_id=actor.id)
    return InvoiceOut.model_validate(invoice)


@router.get("", response_model=PagedResponse[InvoiceOut])
def list_invoices(
    customer_id: int | None = Query(default=None),
    status: InvoiceStatus | None = Query(default=None),
    params: PageParams = Depends(pagination),
    _: User = Depends(require_agent),
    session: Session = Depends(db_session),
) -> dict:
    page = BillingService(session).search(params, customer_id=customer_id, status=status)
    return page.to_dict(lambda i: InvoiceOut.model_validate(i).model_dump())


@router.get("/{invoice_id}", response_model=InvoiceOut)
def get_invoice(
    invoice_id: int,
    _: User = Depends(require_agent),
    session: Session = Depends(db_session),
) -> InvoiceOut:
    return InvoiceOut.model_validate(BillingService(session).get(invoice_id))


@router.post("/{invoice_id}/issue", response_model=InvoiceOut)
def issue_invoice(
    invoice_id: int,
    _: User = Depends(require_agent),
    session: Session = Depends(db_session),
) -> InvoiceOut:
    return InvoiceOut.model_validate(BillingService(session).issue(invoice_id))


@router.post("/{invoice_id}/void", response_model=InvoiceOut)
def void_invoice(
    invoice_id: int,
    _: User = Depends(require_manager),
    session: Session = Depends(db_session),
) -> InvoiceOut:
    return InvoiceOut.model_validate(BillingService(session).void(invoice_id))
