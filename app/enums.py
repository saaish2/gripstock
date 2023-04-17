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
