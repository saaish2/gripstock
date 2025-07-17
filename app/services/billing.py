"""Billing service: invoice generation, payments, and late-fee accrual."""

from __future__ import annotations

from datetime import date, timedelta
from decimal import Decimal

from sqlalchemy.orm import Session

from app.config import get_settings
from app.enums import (
    INVOICE_TRANSITIONS,
    InvoiceStatus,
    PaymentMethod,
    can_transition,
)
from app.errors import BusinessRuleError, ConflictError, InvalidStateError, NotFoundError
from app.models.base import utcnow
from app.models.billing import Invoice, Payment
from app.pagination import Page, PageParams, paginate
from app.repositories.order import InvoiceRepository, OrderRepository, PaymentRepository
from app.services.audit import record_audit
from app.services.customers import CustomerService
from app.services.pricing import late_fee_for
from app.services.references import next_invoice_number

DEFAULT_NET_TERMS_DAYS = 30


class BillingService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.settings = get_settings()
        self.invoices = InvoiceRepository(session)
        self.orders = OrderRepository(session)
        self.payments = PaymentRepository(session)
        self.customers = CustomerService(session)

    def create_for_order(self, order_id: int, actor_id: int | None = None) -> Invoice:
        order = self.orders.get(order_id)
        if order is None:
            raise NotFoundError(f"order {order_id} not found")
        if self.invoices.for_order(order_id) is not None:
            raise ConflictError("an invoice already exists for this order")
        invoice = Invoice(
            number=next_invoice_number(self.session),
            customer_id=order.customer_id,
            order_id=order.id,
            status=InvoiceStatus.DRAFT,
            subtotal=order.grand_total,
            tax_total=Decimal("0.00"),
        )
        invoice.recalculate_total()
        self.invoices.add(invoice)
        record_audit(
            self.session,
            actor_id=actor_id,
            action="invoice.created",
            entity_type="invoice",
            entity_id=invoice.id,
            payload={"number": invoice.number, "total": str(invoice.total)},
        )
        return invoice
