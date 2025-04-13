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

    def search_query(
        self, customer_id: int | None = None, status: OrderStatus | None = None
    ) -> Select:
        stmt = select(RentalOrder)
        if customer_id is not None:
            stmt = stmt.where(RentalOrder.customer_id == customer_id)
        if status is not None:
            stmt = stmt.where(RentalOrder.status == status)
        return stmt.order_by(RentalOrder.created_at.desc())

    def lines_for(self, order_id: int) -> list[OrderLine]:
        stmt = select(OrderLine).where(OrderLine.order_id == order_id)
        return list(self.session.execute(stmt).scalars().all())


class InvoiceRepository(BaseRepository[Invoice]):
    model = Invoice

    def get_by_number(self, number: str) -> Invoice | None:
        stmt = select(Invoice).where(Invoice.number == number)
        return self.session.execute(stmt).scalar_one_or_none()

    def search_query(
        self, customer_id: int | None = None, status: InvoiceStatus | None = None
    ) -> Select:
        stmt = select(Invoice)
        if customer_id is not None:
            stmt = stmt.where(Invoice.customer_id == customer_id)
        if status is not None:
            stmt = stmt.where(Invoice.status == status)
        return stmt.order_by(Invoice.created_at.desc())

    def overdue_as_of(self, as_of: date) -> list[Invoice]:
        stmt = select(Invoice).where(
            Invoice.status.in_([InvoiceStatus.ISSUED, InvoiceStatus.PARTIALLY_PAID]),
            Invoice.due_on.is_not(None),
            Invoice.due_on < as_of,
        )
        return list(self.session.execute(stmt).scalars().all())

    def for_order(self, order_id: int) -> Invoice | None:
        stmt = select(Invoice).where(Invoice.order_id == order_id)
        return self.session.execute(stmt).scalar_one_or_none()


class PaymentRepository(BaseRepository[Payment]):
    model = Payment
