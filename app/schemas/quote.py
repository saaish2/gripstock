"""Quote schemas — price a rental window without persisting anything."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator

from app.schemas.common import ORMModel


class QuoteRequest(BaseModel):
    customer_id: int | None = None
    starts_at: datetime
    ends_at: datetime
    asset_ids: list[int] = Field(min_length=1)
    bundle_discount: Decimal = Field(default=Decimal("0"), ge=0, le=1)

    @model_validator(mode="after")
    def _check_window(self) -> QuoteRequest:
        if self.ends_at <= self.starts_at:
            raise ValueError("ends_at must be after starts_at")
        return self


class QuoteLineOut(BaseModel):
    asset_id: int
    asset_name: str
    rental_days: int
    base_rate: Decimal
    seasonal_rate: Decimal
    discount_amount: Decimal
    deposit_amount: Decimal
    net: Decimal


class QuoteOut(ORMModel):
    starts_at: datetime
    ends_at: datetime
