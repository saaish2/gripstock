"""Service tests for the availability calendar."""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from app.errors import NotFoundError, ValidationError
from app.models.catalog import Asset, Category
from app.models.customer import Customer
from app.services.availability import AvailabilityService
from app.services.reservations import ReservationService
