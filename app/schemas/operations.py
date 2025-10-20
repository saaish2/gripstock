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
    performed_at: datetime


class DamageReportOut(ORMModel):
    id: int
    asset_id: int
    reservation_id: int | None = None
    severity: DamageSeverity
    description: str
    estimated_repair_cost: Decimal
    billable: bool
    resolved: bool
    created_at: datetime


class MaintenanceCreate(BaseModel):
    asset_id: int
    summary: str = Field(min_length=1, max_length=255)
    details: str | None = None


class MaintenanceUpdate(BaseModel):
    status: MaintenanceStatus | None = None
    labor_cost: Decimal | None = Field(default=None, ge=0)
    parts_cost: Decimal | None = Field(default=None, ge=0)
    details: str | None = None


class MaintenanceOut(ORMModel):
    id: int
    asset_id: int
    status: MaintenanceStatus
    summary: str
    labor_cost: Decimal
    parts_cost: Decimal
    total_cost: Decimal
    opened_at: datetime
    closed_at: datetime | None = None


class ApiKeyCreate(BaseModel):
