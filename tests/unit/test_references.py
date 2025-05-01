"""Unit tests for reference-number generation."""

from __future__ import annotations

from app.services.references import (
    next_invoice_number,
    next_order_reference,
    next_reservation_reference,
)
