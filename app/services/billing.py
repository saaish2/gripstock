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
