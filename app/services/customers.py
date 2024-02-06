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
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = CustomerRepository(session)

    def create(self, data: dict, actor_id: int | None = None) -> Customer:
        customer = Customer(**data)
        self.repo.add(customer)
        record_audit(
            self.session,
            actor_id=actor_id,
            action="customer.created",
            entity_type="customer",
            entity_id=customer.id,
        )
        return customer

    def get(self, customer_id: int) -> Customer:
        customer = self.repo.get_active(customer_id)
        if customer is None:
            raise NotFoundError(f"customer {customer_id} not found")
        return customer

    def update(self, customer_id: int, changes: dict) -> Customer:
        customer = self.get(customer_id)
        for field, value in changes.items():
            if value is not None:
                setattr(customer, field, value)
        self.session.flush()
        return customer

    def change_status(self, customer_id: int, target: CustomerStatus) -> Customer:
        customer = self.get(customer_id)
        if target == customer.status:
            return customer
        allowed = _ALLOWED_STATUS_MOVES.get(customer.status, set())
        if target not in allowed:
            raise InvalidStateError(
                f"cannot move customer from {customer.status} to {target}"
            )
        customer.status = target
        self.session.flush()
        return customer

    def soft_delete(self, customer_id: int) -> None:
        customer = self.get(customer_id)
        if customer.outstanding_balance > 0:
            raise BusinessRuleError("cannot archive a customer with an outstanding balance")
        customer.deleted_at = utcnow()
        customer.status = CustomerStatus.ARCHIVED
        self.session.flush()

    def adjust_balance(self, customer_id: int, delta: Decimal) -> Customer:
        customer = self.get(customer_id)
        new_balance = customer.outstanding_balance + delta
        if new_balance < 0:
            new_balance = Decimal("0.00")
        customer.outstanding_balance = new_balance
        self.session.flush()
        return customer

    def ensure_can_charge(self, customer: Customer, amount: Decimal) -> None:
        if customer.status != CustomerStatus.ACTIVE:
            raise BusinessRuleError(f"customer is {customer.status} and cannot be charged")
        if not customer.can_charge(amount):
            raise BusinessRuleError(
                "charge would exceed the customer's available credit",
            )
