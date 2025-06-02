"""Quoting service.

Produces a non-binding price estimate for a set of assets over a window. It
reuses the pricing engine and applies the customer discount when a customer is
supplied, but writes nothing — handy for the counter staff giving a verbal
quote before a reservation exists.
"""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy.orm import Session

from app.config import get_settings
from app.errors import NotFoundError, ValidationError
from app.repositories.catalog import AssetRepository
from app.repositories.customer import CustomerRepository
from app.services.pricing import AssetRates, build_quote, rental_days_between


class QuoteService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.settings = get_settings()
        self.assets = AssetRepository(session)
        self.customers = CustomerRepository(session)

    def quote(
        self,
        asset_ids: list[int],
        starts_at: datetime,
        ends_at: datetime,
        customer_id: int | None = None,
        bundle_discount: Decimal = Decimal("0"),
    ) -> dict:
        if ends_at <= starts_at:
            raise ValidationError("ends_at must be after starts_at")

        assets = {a.id: a for a in self.assets.list_by_ids(asset_ids)}
        missing = set(asset_ids) - set(assets)
        if missing:
            raise NotFoundError(f"assets not found: {sorted(missing)}")

        customer_discount = Decimal("0")
        if customer_id is not None:
            customer = self.customers.get_active(customer_id)
            if customer is None:
                raise NotFoundError(f"customer {customer_id} not found")
            customer_discount = customer.discount_rate

        rate_cards = [
            AssetRates(
                asset_id=a.id,
                daily_rate=a.daily_rate,
                weekly_rate=a.weekly_rate,
                monthly_rate=a.monthly_rate,
                replacement_value=a.replacement_value,
            )
            for a in assets.values()
        ]
        quote = build_quote(
            rate_cards,
            starts_at,
            ends_at,
            settings=self.settings,
            customer_discount=customer_discount,
            bundle_discount=bundle_discount,
        )

        lines = []
        for priced in quote.lines:
            asset = assets[priced.asset_id]
            lines.append(
                {
                    "asset_id": asset.id,
                    "asset_name": asset.name,
                    "rental_days": priced.rental_days,
                    "base_rate": priced.base_rate,
                    "seasonal_rate": priced.seasonal_rate,
                    "discount_amount": priced.discount_amount,
                    "deposit_amount": priced.deposit_amount,
                    "net": priced.net,
                }
            )

        return {
            "starts_at": starts_at,
            "ends_at": ends_at,
            "rental_days": rental_days_between(starts_at, ends_at),
            "lines": lines,
            "subtotal": quote.subtotal,
            "discount_total": quote.discount_total,
            "deposit_total": quote.deposit_total,
            "net_total": quote.net_total,
        }
