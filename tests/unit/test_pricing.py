"""Unit tests for the pricing engine."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

import pytest

from app.config import get_settings
from app.services.pricing import (
    AssetRates,
    build_quote,
    late_fee_for,
    price_line,
    rental_days_between,
    seasonal_multiplier,
    tiered_base_cost,
)


@pytest.fixture()
def settings():
    return get_settings()


def _rates(daily="100", weekly=None, monthly=None, replacement="1000") -> AssetRates:
    return AssetRates(
        asset_id=1,
        daily_rate=Decimal(daily),
        weekly_rate=Decimal(weekly) if weekly else None,
        monthly_rate=Decimal(monthly) if monthly else None,
        replacement_value=Decimal(replacement),
    )


def test_rental_days_rounds_partial_up():
    start = datetime(2024, 3, 1, 9, 0)
    assert rental_days_between(start, datetime(2024, 3, 1, 12, 0)) == 1
    assert rental_days_between(start, datetime(2024, 3, 2, 9, 0)) == 1
    assert rental_days_between(start, datetime(2024, 3, 2, 10, 0)) == 2


def test_rental_days_minimum_one():
    start = datetime(2024, 3, 1, 9, 0)
    assert rental_days_between(start, start) == 1


def test_seasonal_multiplier_peak_and_offpeak():
    assert seasonal_multiplier(datetime(2024, 7, 1)) == Decimal("1.15")
    assert seasonal_multiplier(datetime(2024, 1, 1)) == Decimal("0.95")
    assert seasonal_multiplier(datetime(2024, 4, 1)) == Decimal("1.00")


def test_tiered_cost_prefers_weekly(settings):
    rates = _rates(daily="100", weekly="500")
    # 7 days straight = 700; one weekly tier = 500.
    assert tiered_base_cost(rates, 7, settings) == Decimal("500")


def test_tiered_cost_never_exceeds_straight_daily(settings):
    rates = _rates(daily="100", weekly="900")  # absurdly high weekly
    assert tiered_base_cost(rates, 7, settings) == Decimal("700")


def test_tiered_cost_combines_month_week_day(settings):
    rates = _rates(daily="100", weekly="500", monthly="1500")
    # 28 + 7 + 2 = 37 days -> 1500 + 500 + 200 = 2200, capped at 3700 straight.
    assert tiered_base_cost(rates, 37, settings) == Decimal("2200")
