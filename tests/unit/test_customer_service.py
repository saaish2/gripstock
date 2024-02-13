"""Service tests for customer lifecycle and credit handling."""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.enums import CustomerStatus
from app.errors import BusinessRuleError, InvalidStateError
from app.services.customers import CustomerService
