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


def test_reservation_happy_path():
    assert can_transition(RESERVATION_TRANSITIONS, ReservationStatus.PENDING, ReservationStatus.CONFIRMED)
    assert can_transition(RESERVATION_TRANSITIONS, ReservationStatus.CONFIRMED, ReservationStatus.PICKED_UP)
    assert can_transition(RESERVATION_TRANSITIONS, ReservationStatus.PICKED_UP, ReservationStatus.RETURNED)
