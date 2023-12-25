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
