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

    def get(self, invoice_id: int) -> Invoice:
        invoice = self.invoices.get(invoice_id)
        if invoice is None:
            raise NotFoundError(f"invoice {invoice_id} not found")
        return invoice

    def _transition(self, invoice: Invoice, target: InvoiceStatus) -> None:
        if not can_transition(INVOICE_TRANSITIONS, invoice.status, target):
            raise InvalidStateError(f"cannot move invoice from {invoice.status} to {target}")
        invoice.status = target

    def issue(self, invoice_id: int, net_terms_days: int = DEFAULT_NET_TERMS_DAYS) -> Invoice:
        invoice = self.get(invoice_id)
        self._transition(invoice, InvoiceStatus.ISSUED)
        today = utcnow().date()
        invoice.issued_on = today
        invoice.due_on = today + timedelta(days=net_terms_days)
        self.customers.adjust_balance(invoice.customer_id, invoice.balance_due)
        self.session.flush()
        return invoice

    def void(self, invoice_id: int) -> Invoice:
        invoice = self.get(invoice_id)
        if invoice.amount_paid > 0:
            raise BusinessRuleError("cannot void an invoice that has received payment")
        previous_balance = invoice.balance_due
        self._transition(invoice, InvoiceStatus.VOID)
        invoice.voided_at = utcnow()
        if invoice.status == InvoiceStatus.VOID and previous_balance > 0:
            self.customers.adjust_balance(invoice.customer_id, -previous_balance)
        self.session.flush()
        return invoice

    def record_payment(
        self,
        invoice_id: int,
        amount: Decimal,
        method: PaymentMethod,
        reference: str | None = None,
        actor_id: int | None = None,
    ) -> Payment:
        invoice = self.get(invoice_id)
        if invoice.status in (InvoiceStatus.DRAFT, InvoiceStatus.VOID):
            raise BusinessRuleError(f"cannot pay a {invoice.status} invoice")
        if amount <= 0:
            raise BusinessRuleError("payment amount must be positive")
        if amount > invoice.balance_due:
            raise BusinessRuleError("payment exceeds the invoice balance due")

        payment = Payment(
            invoice_id=invoice.id,
            amount=amount,
            method=method,
            reference=reference,
            received_at=utcnow(),
        )
        self.payments.add(payment)
        invoice.amount_paid += amount
        self.customers.adjust_balance(invoice.customer_id, -amount)

        if invoice.is_settled:
            self._transition(invoice, InvoiceStatus.PAID)
        else:
            if invoice.status != InvoiceStatus.PARTIALLY_PAID:
                self._transition(invoice, InvoiceStatus.PARTIALLY_PAID)
        self.session.flush()
        record_audit(
            self.session,
            actor_id=actor_id,
            action="invoice.payment_recorded",
            entity_type="invoice",
            entity_id=invoice.id,
            payload={"amount": str(amount), "method": method},
        )
        return payment

    def accrue_late_fee(self, invoice_id: int, daily_rate: Decimal, days_late: int) -> Invoice:
        invoice = self.get(invoice_id)
        fee = late_fee_for(daily_rate, days_late, self.settings)
        if fee <= 0:
            return invoice
        invoice.late_fee_total += fee
        invoice.recalculate_total()
        if invoice.status in (InvoiceStatus.ISSUED, InvoiceStatus.PARTIALLY_PAID):
            self._transition(invoice, InvoiceStatus.OVERDUE)
        self.customers.adjust_balance(invoice.customer_id, fee)
        self.session.flush()
        return invoice

    def add_damage_charge(self, invoice_id: int, amount: Decimal) -> Invoice:
        invoice = self.get(invoice_id)
        if amount <= 0:
            raise BusinessRuleError("damage charge must be positive")
        invoice.damage_total += amount
        invoice.recalculate_total()
        if invoice.status != InvoiceStatus.DRAFT:
            self.customers.adjust_balance(invoice.customer_id, amount)
        self.session.flush()
        return invoice

    def sweep_overdue(self, as_of: date | None = None) -> int:
        as_of = as_of or utcnow().date()
        overdue = self.invoices.overdue_as_of(as_of)
        for invoice in overdue:
            if invoice.status != InvoiceStatus.OVERDUE:
                invoice.status = InvoiceStatus.OVERDUE
        self.session.flush()
        return len(overdue)
