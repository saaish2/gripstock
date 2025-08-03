"""Service tests for billing: invoices, payments, late fees."""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.enums import InvoiceStatus, PaymentMethod
from app.errors import BusinessRuleError
from app.models.billing import Invoice
from app.models.customer import Customer
from app.services.billing import BillingService
