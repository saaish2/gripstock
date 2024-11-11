"""Service tests for reservation availability and lifecycle."""

from __future__ import annotations

from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from app.enums import AssetStatus, ReservationStatus
from app.errors import ConflictError, InvalidStateError, ValidationError
from app.models.catalog import Asset, Category
from app.models.customer import Customer
from app.services.reservations import ReservationService
