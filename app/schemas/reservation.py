"""Reservation schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from app.enums import ReservationStatus
from app.schemas.common import ORMModel


class ReservationLineIn(BaseModel):
    asset_id: int
    kit_id: int | None = None
    quantity: int = Field(default=1, ge=1)
