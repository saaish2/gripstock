"""Operations service: checkout/checkin, inspections, damage, maintenance."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from app.enums import (
    AssetCondition,
    AssetStatus,
    MaintenanceStatus,
    ReservationStatus,
)
from app.errors import BusinessRuleError, InvalidStateError, NotFoundError
from app.models.base import utcnow
from app.models.operations import DamageReport, Inspection, MaintenanceOrder
from app.repositories.catalog import AssetRepository
from app.repositories.operations import (
    DamageReportRepository,
    InspectionRepository,
    MaintenanceRepository,
)
from app.repositories.reservation import ReservationRepository
from app.services.audit import record_audit

# Conditions that route an asset straight into maintenance on check-in.
_MAINTENANCE_CONDITIONS = {AssetCondition.POOR, AssetCondition.UNUSABLE}
