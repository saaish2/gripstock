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
