"""Customer repository."""

from __future__ import annotations

from sqlalchemy import Select, or_, select

from app.enums import CustomerStatus
from app.models.customer import Customer
from app.repositories.base import BaseRepository


class CustomerRepository(BaseRepository[Customer]):
    model = Customer

    def active_query(self) -> Select:
        return select(Customer).where(Customer.deleted_at.is_(None))
