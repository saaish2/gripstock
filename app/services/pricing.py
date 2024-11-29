"""Rental pricing engine.

The engine turns a rental window and a set of assets into priced line items.
It is intentionally pure — no database, no clock — so it can be unit-tested
exhaustively and reused by both the quote endpoint and order creation.

Pricing rules, in order of application:

1. Choose the cheapest tier decomposition (months, then weeks, then days)
   using each asset's configured weekly/monthly rates when present.
2. Apply a seasonal multiplier based on the rental's start month.
3. Apply the customer discount and any kit bundle discount (additive, capped).
4. Compute a refundable deposit as a fraction of the replacement value.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from decimal import ROUND_HALF_UP, Decimal

from app.config import Settings

TWO_PLACES = Decimal("0.01")
