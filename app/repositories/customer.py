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

    def search_query(self, term: str | None, status: CustomerStatus | None) -> Select:
        stmt = self.active_query()
        if term:
            like = f"%{term.lower()}%"
            stmt = stmt.where(
                or_(
                    Customer.name.ilike(like),
                    Customer.contact_email.ilike(like),
                )
            )
        if status is not None:
            stmt = stmt.where(Customer.status == status)
        return stmt.order_by(Customer.name)

    def get_active(self, customer_id: int) -> Customer | None:
        stmt = self.active_query().where(Customer.id == customer_id)
        return self.session.execute(stmt).scalar_one_or_none()
