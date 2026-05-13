"""ORM model exports.

Importing this module registers every table against the shared declarative
``Base.metadata`` so Alembic autogeneration and ``create_all`` see them all.
"""

from app.models.base import Base
from app.models.billing import Invoice, Payment
from app.models.catalog import Asset, Category, Kit, KitItem
from app.models.customer import Customer
from app.models.operations import DamageReport, Inspection, MaintenanceOrder
from app.models.order import OrderLine, RentalOrder
from app.models.platform import (
    ApiKey,
    AuditLog,
    IdempotencyKey,
    WebhookDelivery,
    WebhookEndpoint,
)
from app.models.reservation import Reservation, ReservationLine
from app.models.user import Session, User

__all__ = [
    "Base",
    "User",
    "Session",
    "Customer",
    "Category",
    "Asset",
    "Kit",
    "KitItem",
    "Reservation",
    "ReservationLine",
    "RentalOrder",
    "OrderLine",
    "Invoice",
    "Payment",
    "Inspection",
    "DamageReport",
    "MaintenanceOrder",
    "AuditLog",
    "ApiKey",
    "WebhookEndpoint",
    "WebhookDelivery",
    "IdempotencyKey",
]
