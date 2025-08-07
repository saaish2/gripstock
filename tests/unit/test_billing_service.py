"""Service tests for billing: invoices, payments, late fees."""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.enums import InvoiceStatus, PaymentMethod
from app.errors import BusinessRuleError
from app.models.billing import Invoice
from app.models.customer import Customer
from app.services.billing import BillingService


@pytest.fixture()
def invoice(session) -> Invoice:
    customer = Customer(name="Acme", contact_email="a@b.com", credit_limit=Decimal("10000"))
    session.add(customer)
    session.flush()
    inv = Invoice(
        number="INV-000001",
        customer_id=customer.id,
        status=InvoiceStatus.DRAFT,
        subtotal=Decimal("1000.00"),
    )
    inv.recalculate_total()
    session.add(inv)
    session.flush()
    return inv


def test_issue_sets_due_date_and_balance(session, invoice):
    svc = BillingService(session)
    issued = svc.issue(invoice.id, net_terms_days=30)
    assert issued.status == InvoiceStatus.ISSUED
    assert issued.due_on is not None
    assert issued.balance_due == Decimal("1000.00")


def test_full_payment_marks_paid(session, invoice):
    svc = BillingService(session)
    svc.issue(invoice.id)
    svc.record_payment(invoice.id, Decimal("1000.00"), PaymentMethod.CARD)
    session.refresh(invoice)
    assert invoice.status == InvoiceStatus.PAID
    assert invoice.is_settled


def test_partial_payment_marks_partial(session, invoice):
    svc = BillingService(session)
    svc.issue(invoice.id)
    svc.record_payment(invoice.id, Decimal("400.00"), PaymentMethod.ACH)
    session.refresh(invoice)
    assert invoice.status == InvoiceStatus.PARTIALLY_PAID
    assert invoice.balance_due == Decimal("600.00")


def test_overpayment_rejected(session, invoice):
    svc = BillingService(session)
    svc.issue(invoice.id)
    with pytest.raises(BusinessRuleError):
        svc.record_payment(invoice.id, Decimal("1500.00"), PaymentMethod.CASH)
