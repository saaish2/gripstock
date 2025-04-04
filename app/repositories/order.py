"""Rental order, invoice, and payment repositories."""

from __future__ import annotations

from datetime import date

from sqlalchemy import Select, select

from app.enums import InvoiceStatus, OrderStatus
from app.models.billing import Invoice, Payment
from app.models.order import OrderLine, RentalOrder
from app.repositories.base import BaseRepository


class OrderRepository(BaseRepository[RentalOrder]):
    model = RentalOrder

    def get_by_reference(self, reference: str) -> RentalOrder | None:
        stmt = select(RentalOrder).where(RentalOrder.reference == reference)
        return self.session.execute(stmt).scalar_one_or_none()

    def for_reservation(self, reservation_id: int) -> RentalOrder | None:
        stmt = select(RentalOrder).where(RentalOrder.reservation_id == reservation_id)
        return self.session.execute(stmt).scalar_one_or_none()
