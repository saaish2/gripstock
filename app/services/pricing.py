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

    @property
    def net(self) -> Decimal:
        return self.seasonal_rate - self.discount_amount


def rental_days_between(starts_at: datetime, ends_at: datetime) -> int:
    """Number of chargeable days; any partial day rounds up, minimum one."""

    seconds = (ends_at - starts_at).total_seconds()
    if seconds <= 0:
        return 1
    days = seconds / 86400
    whole = int(days)
    if days - whole > 0:
        whole += 1
    return max(1, whole)


def seasonal_multiplier(starts_at: datetime) -> Decimal:
    return SEASONAL_MULTIPLIERS.get(starts_at.month, Decimal("1.00"))


def tiered_base_cost(rates: AssetRates, days: int, settings: Settings) -> Decimal:
    """Cheapest decomposition of ``days`` into month/week/day tiers."""

    remaining = days
    total = Decimal("0.00")

    month_days = settings.monthly_tier_days
    week_days = settings.weekly_tier_days

    if rates.monthly_rate is not None and remaining >= month_days:
        months = remaining // month_days
        total += months * rates.monthly_rate
        remaining -= months * month_days

    if rates.weekly_rate is not None and remaining >= week_days:
        weeks = remaining // week_days
        total += weeks * rates.weekly_rate
        remaining -= weeks * week_days

    total += remaining * rates.daily_rate

    # Never charge more than the straight daily rate would have cost.
    straight = days * rates.daily_rate
    return min(total, straight)


def price_line(
    rates: AssetRates,
    starts_at: datetime,
    ends_at: datetime,
    *,
    settings: Settings,
    customer_discount: Decimal = Decimal("0"),
    bundle_discount: Decimal = Decimal("0"),
) -> PricedLine:
    """Price a single asset over the rental window."""

    days = rental_days_between(starts_at, ends_at)
    base = tiered_base_cost(rates, days, settings)
    seasonal = _money(base * seasonal_multiplier(starts_at))

    discount_rate = min(customer_discount + bundle_discount, Decimal("0.75"))
    discount = _money(seasonal * discount_rate)

    deposit = _money(rates.replacement_value * settings.default_deposit_rate)

    return PricedLine(
        asset_id=rates.asset_id,
        rental_days=days,
        base_rate=_money(base),
        seasonal_rate=seasonal,
        discount_amount=discount,
        deposit_amount=deposit,
    )


@dataclass(slots=True)
class Quote:
    lines: list[PricedLine]

    @property
    def subtotal(self) -> Decimal:
        return _money(sum((line.seasonal_rate for line in self.lines), Decimal("0.00")))

    @property
    def discount_total(self) -> Decimal:
        return _money(sum((line.discount_amount for line in self.lines), Decimal("0.00")))

    @property
    def deposit_total(self) -> Decimal:
        return _money(sum((line.deposit_amount for line in self.lines), Decimal("0.00")))

    @property
    def net_total(self) -> Decimal:
        return _money(self.subtotal - self.discount_total)


def build_quote(
    rate_cards: list[AssetRates],
    starts_at: datetime,
    ends_at: datetime,
    *,
    settings: Settings,
    customer_discount: Decimal = Decimal("0"),
    bundle_discount: Decimal = Decimal("0"),
) -> Quote:
    lines = [
        price_line(
            card,
            starts_at,
            ends_at,
            settings=settings,
            customer_discount=customer_discount,
            bundle_discount=bundle_discount,
        )
        for card in rate_cards
    ]
    return Quote(lines=lines)
