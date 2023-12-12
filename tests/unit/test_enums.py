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


def test_reservation_terminal_states_are_dead_ends():
    for terminal in (ReservationStatus.RETURNED, ReservationStatus.CANCELLED, ReservationStatus.NO_SHOW):
        assert RESERVATION_TRANSITIONS[terminal] == set()


def test_reservation_illegal_moves():
    assert not can_transition(RESERVATION_TRANSITIONS, ReservationStatus.PENDING, ReservationStatus.RETURNED)
    assert not can_transition(RESERVATION_TRANSITIONS, ReservationStatus.RETURNED, ReservationStatus.PENDING)
