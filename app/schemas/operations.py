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
