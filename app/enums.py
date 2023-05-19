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


# Allowed transitions per state machine. A move is legal iff the target is in
# the set keyed by the current state.
RESERVATION_TRANSITIONS: dict[ReservationStatus, set[ReservationStatus]] = {
    ReservationStatus.PENDING: {
        ReservationStatus.CONFIRMED,
        ReservationStatus.CANCELLED,
    },
    ReservationStatus.CONFIRMED: {
        ReservationStatus.PICKED_UP,
        ReservationStatus.CANCELLED,
        ReservationStatus.NO_SHOW,
    },
    ReservationStatus.PICKED_UP: {
        ReservationStatus.RETURNED,
        ReservationStatus.OVERDUE,
    },
    ReservationStatus.OVERDUE: {
        ReservationStatus.RETURNED,
    },
    ReservationStatus.RETURNED: set(),
    ReservationStatus.CANCELLED: set(),
    ReservationStatus.NO_SHOW: set(),
}

ASSET_TRANSITIONS: dict[AssetStatus, set[AssetStatus]] = {
    AssetStatus.AVAILABLE: {
        AssetStatus.RESERVED,
        AssetStatus.CHECKED_OUT,
        AssetStatus.IN_MAINTENANCE,
        AssetStatus.RETIRED,
        AssetStatus.LOST,
    },
    AssetStatus.RESERVED: {
        AssetStatus.CHECKED_OUT,
        AssetStatus.AVAILABLE,
        AssetStatus.LOST,
    },
    AssetStatus.CHECKED_OUT: {
        AssetStatus.AVAILABLE,
        AssetStatus.IN_MAINTENANCE,
        AssetStatus.LOST,
    },
    AssetStatus.IN_MAINTENANCE: {
        AssetStatus.AVAILABLE,
        AssetStatus.RETIRED,
    },
    AssetStatus.RETIRED: set(),
    AssetStatus.LOST: {AssetStatus.AVAILABLE},
}

INVOICE_TRANSITIONS: dict[InvoiceStatus, set[InvoiceStatus]] = {
    InvoiceStatus.DRAFT: {InvoiceStatus.ISSUED, InvoiceStatus.VOID},
    InvoiceStatus.ISSUED: {
        InvoiceStatus.PARTIALLY_PAID,
        InvoiceStatus.PAID,
        InvoiceStatus.OVERDUE,
        InvoiceStatus.VOID,
    },
    InvoiceStatus.PARTIALLY_PAID: {
        InvoiceStatus.PAID,
        InvoiceStatus.OVERDUE,
        InvoiceStatus.VOID,
    },
    InvoiceStatus.OVERDUE: {
        InvoiceStatus.PARTIALLY_PAID,
        InvoiceStatus.PAID,
        InvoiceStatus.VOID,
    },
    InvoiceStatus.PAID: set(),
    InvoiceStatus.VOID: set(),
}
