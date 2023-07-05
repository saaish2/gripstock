"""Customer (production company) ORM model."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy import Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.enums import CustomerStatus
from app.models.base import Base, IntPrimaryKey, SoftDeleteMixin, TimestampMixin
