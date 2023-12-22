"""Customer schemas."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, EmailStr, Field

from app.enums import CustomerStatus
from app.schemas.common import ORMModel


class CustomerCreate(BaseModel):
