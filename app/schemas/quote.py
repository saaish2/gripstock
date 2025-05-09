"""Quote schemas — price a rental window without persisting anything."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field, model_validator

from app.schemas.common import ORMModel


class QuoteRequest(BaseModel):
    customer_id: int | None = None
