"""Unit tests for reference-number generation."""

from __future__ import annotations

from app.services.references import (
    next_invoice_number,
    next_order_reference,
    next_reservation_reference,
)


def test_reservation_reference_format(session):
    ref = next_reservation_reference(session)
    assert ref.startswith("RSV-")
    assert ref == "RSV-001001"


def test_order_reference_format(session):
    assert next_order_reference(session) == "ORD-001001"
