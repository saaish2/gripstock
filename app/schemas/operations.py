"""Operational schemas: inspections, damage, maintenance, webhooks, api keys."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.enums import (
    AssetCondition,
    DamageSeverity,
    MaintenanceStatus,
    WebhookStatus,
)
from app.schemas.common import ORMModel


class CheckoutLine(BaseModel):
    asset_id: int
    condition: AssetCondition = AssetCondition.GOOD
    notes: str | None = None


class CheckinLine(BaseModel):
    asset_id: int
    condition: AssetCondition
    notes: str | None = None
    damage_severity: DamageSeverity | None = None
    damage_description: str | None = None
    estimated_repair_cost: Decimal = Field(default=Decimal("0.00"), ge=0)


class InspectionOut(ORMModel):
    id: int
    reservation_id: int
    asset_id: int
    phase: str
    condition: AssetCondition
