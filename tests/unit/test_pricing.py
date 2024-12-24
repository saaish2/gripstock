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
