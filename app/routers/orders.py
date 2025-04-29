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

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("", response_model=OrderOut, status_code=201)
def create_order(
    payload: OrderFromReservation,
    actor: User = Depends(require_agent),
    session: Session = Depends(db_session),
    idempotency_key: str | None = Header(default=None),
) -> OrderOut:
    def _build() -> OrderOut:
        order = OrderService(session).create_from_reservation(
            payload.reservation_id, tax_rate=payload.tax_rate, actor_id=actor.id
        )
        return OrderOut.model_validate(order)

    return idempotent(
        session,
        key=idempotency_key,
        method="POST",
        path="/orders",
        producer=_build,
    )


@router.get("", response_model=PagedResponse[OrderOut])
def list_orders(
    customer_id: int | None = Query(default=None),
    status: OrderStatus | None = Query(default=None),
    params: PageParams = Depends(pagination),
    _: User = Depends(require_agent),
    session: Session = Depends(db_session),
) -> dict:
    page = OrderService(session).search(params, customer_id=customer_id, status=status)
    return page.to_dict(lambda o: OrderOut.model_validate(o).model_dump())


@router.get("/{order_id}", response_model=OrderOut)
def get_order(
    order_id: int,
    _: User = Depends(require_agent),
    session: Session = Depends(db_session),
) -> OrderOut:
    return OrderOut.model_validate(OrderService(session).get(order_id))


@router.post("/{order_id}/open", response_model=OrderOut)
def open_order(
    order_id: int,
    _: User = Depends(require_agent),
    session: Session = Depends(db_session),
) -> OrderOut:
    return OrderOut.model_validate(OrderService(session).open(order_id))


@router.post("/{order_id}/close", response_model=OrderOut)
def close_order(
    order_id: int,
    _: User = Depends(require_agent),
    session: Session = Depends(db_session),
) -> OrderOut:
    return OrderOut.model_validate(OrderService(session).close(order_id))
