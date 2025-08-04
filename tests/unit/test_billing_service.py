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
