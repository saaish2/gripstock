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
