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
