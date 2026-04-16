"""Reporting and dashboard-statistics service.

These read-only aggregations power the operations dashboard: utilisation,
revenue, overdue exposure, and inventory health. They are deliberately
expressed as SQL aggregates so they stay cheap on large datasets.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.enums import AssetStatus, InvoiceStatus, MaintenanceStatus, ReservationStatus
from app.models.billing import Invoice
from app.models.catalog import Asset, Category
from app.models.customer import Customer
from app.models.operations import MaintenanceOrder
from app.models.reservation import Reservation


@dataclass(slots=True)
class InventorySnapshot:
    total: int
    by_status: dict[str, int] = field(default_factory=dict)

    @property
    def utilisation(self) -> float:
        if self.total == 0:
            return 0.0
        in_use = self.by_status.get(AssetStatus.CHECKED_OUT, 0)
        reserved = self.by_status.get(AssetStatus.RESERVED, 0)
        return round((in_use + reserved) / self.total, 4)


class ReportService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def inventory_snapshot(self) -> InventorySnapshot:
        rows = self.session.execute(
            select(Asset.status, func.count())
            .where(Asset.deleted_at.is_(None))
            .group_by(Asset.status)
        ).all()
        by_status = {str(status): count for status, count in rows}
        total = sum(by_status.values())
        return InventorySnapshot(total=total, by_status=by_status)

    def revenue_summary(self) -> dict[str, Decimal]:
        billed = self.session.execute(
            select(func.coalesce(func.sum(Invoice.total), 0)).where(
                Invoice.status != InvoiceStatus.VOID
            )
        ).scalar_one()
        collected = self.session.execute(
            select(func.coalesce(func.sum(Invoice.amount_paid), 0))
        ).scalar_one()
        return {
            "billed": Decimal(str(billed)),
            "collected": Decimal(str(collected)),
            "outstanding": Decimal(str(billed)) - Decimal(str(collected)),
        }

    def overdue_exposure(self) -> dict[str, object]:
        rows = self.session.execute(
            select(func.count(), func.coalesce(func.sum(Invoice.total - Invoice.amount_paid), 0))
            .where(Invoice.status == InvoiceStatus.OVERDUE)
        ).one()
        count, amount = rows
        return {"count": count, "amount": Decimal(str(amount))}

    def active_reservations(self, now: datetime) -> int:
        return self.session.execute(
            select(func.count()).where(
                Reservation.status.in_(
                    [
                        ReservationStatus.CONFIRMED,
                        ReservationStatus.PICKED_UP,
                        ReservationStatus.OVERDUE,
                    ]
                )
            )
        ).scalar_one()

    def revenue_by_category(self) -> list[dict]:
        """Billed revenue grouped by the category of each invoiced asset.

        Walks invoice → order → order_lines → asset → category and sums the
        line subtotals so finance can see which gear types earn their keep.
        """

        from app.models.order import OrderLine, RentalOrder

        rows = self.session.execute(
            select(Category.name, func.coalesce(func.sum(OrderLine.line_subtotal), 0))
            .join(Asset, Asset.category_id == Category.id)
            .join(OrderLine, OrderLine.asset_id == Asset.id)
            .join(RentalOrder, RentalOrder.id == OrderLine.order_id)
            .join(Invoice, Invoice.order_id == RentalOrder.id)
            .where(Invoice.status != InvoiceStatus.VOID)
            .group_by(Category.name)
            .order_by(func.sum(OrderLine.line_subtotal).desc())
        ).all()
        return [{"category": name, "revenue": Decimal(str(total))} for name, total in rows]
