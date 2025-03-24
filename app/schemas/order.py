"""Rental order and billing schemas."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.enums import InvoiceStatus, OrderStatus, PaymentMethod
from app.schemas.common import ORMModel


class OrderFromReservation(BaseModel):
    reservation_id: int
    tax_rate: Decimal = Field(default=Decimal("0.0000"), ge=0, le=1)


class OrderLineOut(ORMModel):
    id: int
    asset_id: int
    description: str
    quantity: int
    rental_days: int
    unit_rate: Decimal
    line_subtotal: Decimal
    discount_amount: Decimal
    deposit_amount: Decimal


class OrderOut(ORMModel):
    id: int
    reference: str
    customer_id: int
    reservation_id: int | None = None
    status: OrderStatus
    starts_at: datetime
    ends_at: datetime
    subtotal: Decimal
    discount_total: Decimal
    deposit_total: Decimal
    tax_total: Decimal
    grand_total: Decimal
    lines: list[OrderLineOut] = Field(default_factory=list)
    created_at: datetime


class InvoiceOut(ORMModel):
    id: int
    number: str
    customer_id: int
    order_id: int | None = None
    status: InvoiceStatus
    issued_on: date | None = None
    due_on: date | None = None
    subtotal: Decimal
    late_fee_total: Decimal
    damage_total: Decimal
    tax_total: Decimal
    total: Decimal
    amount_paid: Decimal
    balance_due: Decimal
    created_at: datetime


class PaymentCreate(BaseModel):
    amount: Decimal = Field(gt=0)
    method: PaymentMethod
    reference: str | None = Field(default=None, max_length=120)
