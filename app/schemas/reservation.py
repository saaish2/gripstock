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


class ReservationCreate(BaseModel):
    customer_id: int
    starts_at: datetime
    ends_at: datetime
    notes: str | None = None
    lines: list[ReservationLineIn] = Field(min_length=1)

    @model_validator(mode="after")
    def _check_window(self) -> ReservationCreate:
        if self.ends_at <= self.starts_at:
            raise ValueError("ends_at must be after starts_at")
        return self


class ReservationReschedule(BaseModel):
    starts_at: datetime
    ends_at: datetime

    @model_validator(mode="after")
    def _check_window(self) -> ReservationReschedule:
        if self.ends_at <= self.starts_at:
            raise ValueError("ends_at must be after starts_at")
        return self


class ReservationLineOut(ORMModel):
    id: int
    asset_id: int
    kit_id: int | None = None
    quantity: int


class ReservationOut(ORMModel):
    id: int
    reference: str
    customer_id: int
    status: ReservationStatus
    starts_at: datetime
