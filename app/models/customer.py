"""Customer (production company) ORM model."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.enums import CustomerStatus
from app.models.base import Base, IntPrimaryKey, SoftDeleteMixin, TimestampMixin


class Customer(Base, IntPrimaryKey, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "customers"

    name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    contact_email: Mapped[str] = mapped_column(String(255), nullable=False)
    contact_phone: Mapped[str | None] = mapped_column(String(40), nullable=True)
    billing_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    tax_id: Mapped[str | None] = mapped_column(String(40), nullable=True)
    status: Mapped[CustomerStatus] = mapped_column(
        String(20), default=CustomerStatus.ACTIVE, nullable=False
    )
    credit_limit: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=Decimal("0.00"), nullable=False
    )
    outstanding_balance: Mapped[Decimal] = mapped_column(
        Numeric(12, 2), default=Decimal("0.00"), nullable=False
    )
    discount_rate: Mapped[Decimal] = mapped_column(
        Numeric(5, 4), default=Decimal("0.0000"), nullable=False
    )
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    reservations: Mapped[list[Reservation]] = relationship(back_populates="customer")  # noqa: F821
    orders: Mapped[list[RentalOrder]] = relationship(back_populates="customer")  # noqa: F821

    @property
    def available_credit(self) -> Decimal:
        return self.credit_limit - self.outstanding_balance

    def can_charge(self, amount: Decimal) -> bool:
        if self.status != CustomerStatus.ACTIVE:
            return False
        return self.available_credit >= amount
