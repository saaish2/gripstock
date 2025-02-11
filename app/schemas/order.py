"""Rental order and billing schemas."""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.enums import InvoiceStatus, OrderStatus, PaymentMethod
from app.schemas.common import ORMModel


class OrderFromReservation(BaseModel):
    reservation_id: int
