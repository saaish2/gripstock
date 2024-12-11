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

# Peak production months (summer + holiday) carry a surcharge.
SEASONAL_MULTIPLIERS: dict[int, Decimal] = {
    1: Decimal("0.95"),
    6: Decimal("1.10"),
    7: Decimal("1.15"),
    8: Decimal("1.10"),
    11: Decimal("1.05"),
    12: Decimal("1.10"),
}


def _money(value: Decimal) -> Decimal:
    return value.quantize(TWO_PLACES, rounding=ROUND_HALF_UP)


@dataclass(slots=True)
class AssetRates:
    """The pricing-relevant fields lifted off an asset row."""

    asset_id: int
    daily_rate: Decimal
    weekly_rate: Decimal | None
    monthly_rate: Decimal | None
    replacement_value: Decimal


@dataclass(slots=True)
class PricedLine:
    asset_id: int
    rental_days: int
    base_rate: Decimal
    seasonal_rate: Decimal
    discount_amount: Decimal
    deposit_amount: Decimal
