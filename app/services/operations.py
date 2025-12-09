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


class CheckoutService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.reservations = ReservationRepository(session)
        self.assets = AssetRepository(session)
        self.inspections = InspectionRepository(session)
        self.damage = DamageReportRepository(session)

    def check_out(self, reservation_id: int, lines: list[dict], actor_id: int | None = None):
        reservation = self.reservations.get(reservation_id)
        if reservation is None:
            raise NotFoundError(f"reservation {reservation_id} not found")
        if reservation.status != ReservationStatus.CONFIRMED:
            raise InvalidStateError("only confirmed reservations can be checked out")

        line_by_asset = {line["asset_id"]: line for line in lines}
        now = utcnow()
        for res_line in reservation.lines:
            asset = self.assets.get(res_line.asset_id)
            if asset is None:
                raise NotFoundError(f"asset {res_line.asset_id} not found")
            payload = line_by_asset.get(asset.id, {})
            condition = payload.get("condition", AssetCondition.GOOD)
            self.inspections.add(
                Inspection(
                    reservation_id=reservation.id,
                    asset_id=asset.id,
                    phase="checkout",
                    condition=condition,
                    inspector_id=actor_id,
                    performed_at=now,
                    notes=payload.get("notes"),
                )
            )
            asset.status = AssetStatus.CHECKED_OUT

        reservation.status = ReservationStatus.PICKED_UP
        reservation.picked_up_at = now
        self.session.flush()
        record_audit(
            self.session,
            actor_id=actor_id,
            action="reservation.checked_out",
            entity_type="reservation",
            entity_id=reservation.id,
        )
        return reservation

    def check_in(self, reservation_id: int, lines: list[dict], actor_id: int | None = None):
        reservation = self.reservations.get(reservation_id)
        if reservation is None:
            raise NotFoundError(f"reservation {reservation_id} not found")
        if reservation.status not in (ReservationStatus.PICKED_UP, ReservationStatus.OVERDUE):
            raise InvalidStateError("only picked-up reservations can be checked in")

        line_by_asset = {line["asset_id"]: line for line in lines}
        now = utcnow()
        damage_reports: list[DamageReport] = []
        for res_line in reservation.lines:
            asset = self.assets.get(res_line.asset_id)
            if asset is None:
                raise NotFoundError(f"asset {res_line.asset_id} not found")
            payload = line_by_asset.get(asset.id)
            if payload is None:
                raise BusinessRuleError(f"asset {asset.id} was not included in check-in")
            condition = payload["condition"]
            self.inspections.add(
                Inspection(
                    reservation_id=reservation.id,
                    asset_id=asset.id,
                    phase="checkin",
                    condition=condition,
                    inspector_id=actor_id,
                    performed_at=now,
                    notes=payload.get("notes"),
                )
            )
            asset.condition = condition
            if payload.get("damage_severity"):
                report = DamageReport(
                    asset_id=asset.id,
                    reservation_id=reservation.id,
                    severity=payload["damage_severity"],
                    description=payload.get("damage_description", "damage on return"),
                    estimated_repair_cost=payload.get("estimated_repair_cost", Decimal("0.00")),
                    reported_by_id=actor_id,
                )
                self.damage.add(report)
                damage_reports.append(report)

            if condition in _MAINTENANCE_CONDITIONS or payload.get("damage_severity"):
                asset.status = AssetStatus.IN_MAINTENANCE
            else:
                asset.status = AssetStatus.AVAILABLE

        reservation.status = ReservationStatus.RETURNED
        reservation.returned_at = now
        self.session.flush()
        record_audit(
            self.session,
            actor_id=actor_id,
            action="reservation.checked_in",
            entity_type="reservation",
            entity_id=reservation.id,
            payload={"damage_reports": len(damage_reports)},
        )
        return reservation, damage_reports


class MaintenanceService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = MaintenanceRepository(session)
        self.assets = AssetRepository(session)
