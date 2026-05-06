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

CATEGORIES = [
    ("Cameras", "Cinema and mirrorless camera bodies"),
    ("Lenses", "Prime and zoom cinema lenses"),
    ("Lighting", "LED panels, HMIs, and tungsten fixtures"),
    ("Grip", "Stands, clamps, flags, and rigging"),
    ("Audio", "Recorders, mics, and wireless kits"),
]

ASSETS = [
    ("Cameras", "ARRI Alexa Mini", "ARRI", "AMIRA-001", Decimal("650"), Decimal("48000")),
    ("Cameras", "RED Komodo 6K", "RED", "KMD-014", Decimal("450"), Decimal("32000")),
    ("Lenses", "Zeiss Supreme 50mm", "Zeiss", "ZS-050", Decimal("120"), Decimal("18000")),
    ("Lighting", "Aputure 600d Pro", "Aputure", "AP-600", Decimal("85"), Decimal("1900")),
    ("Grip", "C-Stand 40in", "Matthews", "CS-040", Decimal("12"), Decimal("260")),
    ("Audio", "Sound Devices MixPre-6", "Sound Devices", "SD-006", Decimal("70"), Decimal("1200")),
]
