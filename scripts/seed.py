"""Idempotent demo-data seeder.

Loads a small but coherent dataset: an admin user, a handful of categories and
assets, a couple of customers, and one fully-worked rental so the dashboard
shows non-zero numbers immediately after ``gripstock seed``.
"""

from __future__ import annotations

from datetime import timedelta
from decimal import Decimal

from sqlalchemy.orm import Session

from app.enums import Role
from app.models.base import utcnow
from app.repositories.user import UserRepository
from app.services.auth import AuthService
from app.services.catalog import AssetService, CategoryService
from app.services.customers import CustomerService
from app.services.reservations import ReservationService
