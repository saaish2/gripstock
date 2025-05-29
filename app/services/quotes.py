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
