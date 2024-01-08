"""Customer schemas."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field

from app.enums import CustomerStatus
from app.schemas.common import ORMModel


class CustomerCreate(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    contact_email: EmailStr
    contact_phone: str | None = Field(default=None, max_length=40)
    billing_address: str | None = None
    tax_id: str | None = Field(default=None, max_length=40)
    credit_limit: Decimal = Field(default=Decimal("0.00"), ge=0)
    discount_rate: Decimal = Field(default=Decimal("0.0000"), ge=0, le=1)
    notes: str | None = None


class CustomerUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=255)
    contact_email: EmailStr | None = None
    contact_phone: str | None = Field(default=None, max_length=40)
    billing_address: str | None = None
    credit_limit: Decimal | None = Field(default=None, ge=0)
    discount_rate: Decimal | None = Field(default=None, ge=0, le=1)
