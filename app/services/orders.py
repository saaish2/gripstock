"""Rental order service — turns a confirmed reservation into a priced order."""

from __future__ import annotations

from decimal import Decimal

from sqlalchemy.orm import Session

from app.config import get_settings
from app.enums import OrderStatus, ReservationStatus
from app.errors import BusinessRuleError, ConflictError, NotFoundError
from app.models.order import OrderLine, RentalOrder
from app.pagination import Page, PageParams, paginate
from app.repositories.catalog import AssetRepository, KitRepository
from app.repositories.customer import CustomerRepository
from app.repositories.order import OrderRepository
from app.repositories.reservation import ReservationRepository
from app.services.audit import record_audit
from app.services.pricing import AssetRates, build_quote
from app.services.references import next_order_reference


class OrderService:
