"""Service tests for customer lifecycle and credit handling."""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.enums import CustomerStatus
from app.errors import BusinessRuleError, InvalidStateError
from app.services.customers import CustomerService


def _make(session, **overrides) -> int:
    svc = CustomerService(session)
    data = {
        "name": "Test Co",
        "contact_email": "t@e.com",
        "credit_limit": Decimal("1000.00"),
    }
    data.update(overrides)
    return svc.create(data).id


def test_status_transition_allowed(session):
    svc = CustomerService(session)
    cid = _make(session)
    svc.change_status(cid, CustomerStatus.ON_HOLD)
    customer = svc.get(cid)
    assert customer.status == CustomerStatus.ON_HOLD


def test_status_transition_blocked(session):
    svc = CustomerService(session)
    cid = _make(session)
    svc.change_status(cid, CustomerStatus.ARCHIVED)
    with pytest.raises(InvalidStateError):
        svc.change_status(cid, CustomerStatus.ACTIVE)


def test_can_charge_within_credit(session):
    svc = CustomerService(session)
    cid = _make(session, credit_limit=Decimal("500.00"))
    customer = svc.get(cid)
    svc.ensure_can_charge(customer, Decimal("400.00"))


def test_charge_exceeding_credit_rejected(session):
    svc = CustomerService(session)
    cid = _make(session, credit_limit=Decimal("100.00"))
    customer = svc.get(cid)
    with pytest.raises(BusinessRuleError):
        svc.ensure_can_charge(customer, Decimal("200.00"))
