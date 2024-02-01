"""Customer management service."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from app.enums import CustomerStatus
from app.errors import BusinessRuleError, InvalidStateError, NotFoundError
from app.models.base import utcnow
from app.models.customer import Customer
from app.pagination import Page, PageParams, paginate
from app.repositories.customer import CustomerRepository
from app.services.audit import record_audit

# Status moves the front desk is allowed to make directly.
_ALLOWED_STATUS_MOVES: dict[CustomerStatus, set[CustomerStatus]] = {
    CustomerStatus.ACTIVE: {CustomerStatus.ON_HOLD, CustomerStatus.BLOCKED, CustomerStatus.ARCHIVED},
    CustomerStatus.ON_HOLD: {CustomerStatus.ACTIVE, CustomerStatus.BLOCKED},
    CustomerStatus.BLOCKED: {CustomerStatus.ACTIVE, CustomerStatus.ARCHIVED},
    CustomerStatus.ARCHIVED: set(),
}


class CustomerService:
