"""Unit tests for state-machine transition tables."""

from __future__ import annotations

from app.enums import (
    ASSET_TRANSITIONS,
    INVOICE_TRANSITIONS,
    RESERVATION_TRANSITIONS,
    AssetStatus,
    InvoiceStatus,
    ReservationStatus,
    can_transition,
)
