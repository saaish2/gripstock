"""Operational repositories: inspections, damage, maintenance, platform."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Select, select

from app.enums import MaintenanceStatus, WebhookStatus
from app.models.operations import DamageReport, Inspection, MaintenanceOrder
from app.models.platform import (
    ApiKey,
    AuditLog,
    IdempotencyKey,
    WebhookDelivery,
    WebhookEndpoint,
)
from app.repositories.base import BaseRepository


class InspectionRepository(BaseRepository[Inspection]):
    model = Inspection

    def for_reservation(self, reservation_id: int) -> list[Inspection]:
        stmt = select(Inspection).where(Inspection.reservation_id == reservation_id)
        return list(self.session.execute(stmt).scalars().all())


class DamageReportRepository(BaseRepository[DamageReport]):
    model = DamageReport

    def unresolved(self) -> list[DamageReport]:
        stmt = select(DamageReport).where(DamageReport.resolved.is_(False))
        return list(self.session.execute(stmt).scalars().all())

    def for_reservation(self, reservation_id: int) -> list[DamageReport]:
        stmt = select(DamageReport).where(DamageReport.reservation_id == reservation_id)
        return list(self.session.execute(stmt).scalars().all())


class MaintenanceRepository(BaseRepository[MaintenanceOrder]):
    model = MaintenanceOrder
