"""Reservation schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field, model_validator

from app.enums import ReservationStatus
from app.schemas.common import ORMModel


class ReservationLineIn(BaseModel):
