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

    def open_for_asset(self, asset_id: int) -> list[MaintenanceOrder]:
        stmt = select(MaintenanceOrder).where(
            MaintenanceOrder.asset_id == asset_id,
            MaintenanceOrder.status.in_(
                [MaintenanceStatus.OPEN, MaintenanceStatus.IN_PROGRESS]
            ),
        )
        return list(self.session.execute(stmt).scalars().all())

    def search_query(self, status: MaintenanceStatus | None = None) -> Select:
        stmt = select(MaintenanceOrder)
        if status is not None:
            stmt = stmt.where(MaintenanceOrder.status == status)
        return stmt.order_by(MaintenanceOrder.opened_at.desc())


class AuditLogRepository(BaseRepository[AuditLog]):
    model = AuditLog
