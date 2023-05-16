"""Enumerations shared across the domain.

State machines are expressed as plain string enums plus an adjacency table of
allowed transitions. Keeping the transition rules next to the enum means the
service layer can validate a move with a single membership test.
"""

from __future__ import annotations

from enum import StrEnum


class Role(StrEnum):
    ADMIN = "admin"
    MANAGER = "manager"
    AGENT = "agent"
    VIEWER = "viewer"


class CustomerStatus(StrEnum):
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    BLOCKED = "blocked"
    ARCHIVED = "archived"


class AssetStatus(StrEnum):
    AVAILABLE = "available"
    RESERVED = "reserved"
    CHECKED_OUT = "checked_out"
    IN_MAINTENANCE = "in_maintenance"
    RETIRED = "retired"
    LOST = "lost"


class AssetCondition(StrEnum):
    NEW = "new"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    UNUSABLE = "unusable"


class ReservationStatus(StrEnum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PICKED_UP = "picked_up"
    RETURNED = "returned"
    CANCELLED = "cancelled"
    OVERDUE = "overdue"
    NO_SHOW = "no_show"


class OrderStatus(StrEnum):
    DRAFT = "draft"
    OPEN = "open"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class InvoiceStatus(StrEnum):
    DRAFT = "draft"
    ISSUED = "issued"
    PARTIALLY_PAID = "partially_paid"
    PAID = "paid"
    OVERDUE = "overdue"
    VOID = "void"


class PaymentMethod(StrEnum):
    CARD = "card"
    ACH = "ach"
    CASH = "cash"
    CHECK = "check"
    CREDIT = "account_credit"


class DamageSeverity(StrEnum):
    COSMETIC = "cosmetic"
    MINOR = "minor"
    MAJOR = "major"
    TOTAL = "total"


class MaintenanceStatus(StrEnum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class WebhookStatus(StrEnum):
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
    DISABLED = "disabled"
