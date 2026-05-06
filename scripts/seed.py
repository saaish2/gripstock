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


def seed_all(session: Session) -> dict:
    auth = AuthService(session)
    users = UserRepository(session)
    if users.get_by_email("admin@gripstock.com") is None:
        auth.create_user(
            email="admin@gripstock.com",
            full_name="Gripstock Admin",
            password="changeit-please",
            role=Role.ADMIN,
        )

    categories = CategoryService(session)
    cat_by_name: dict[str, int] = {}
    for name, description in CATEGORIES:
        existing = categories.repo.get_by_slug(name.lower())
        if existing is None:
            created = categories.create(name, description=description)
            cat_by_name[name] = created.id
        else:
            cat_by_name[name] = existing.id

    assets = AssetService(session)
    asset_ids: list[int] = []
    for cat_name, name, manufacturer, barcode, daily, replacement in ASSETS:
        if assets.repo.get_by_barcode(barcode) is not None:
            continue
        created = assets.create(
            {
                "category_id": cat_by_name[cat_name],
                "name": name,
                "manufacturer": manufacturer,
                "barcode": barcode,
                "daily_rate": daily,
                "weekly_rate": daily * 5,
                "replacement_value": replacement,
                "condition": "good",
            }
        )
        asset_ids.append(created.id)

    customers = CustomerService(session)
    if not customers.repo.list():
        customers.create(
            {
                "name": "Lantern House Films",
                "contact_email": "ops@lanternhouse.com",
                "credit_limit": Decimal("25000"),
                "discount_rate": Decimal("0.05"),
            }
        )
        customers.create(
            {
                "name": "Northwind Studios",
                "contact_email": "rentals@northwind.com",
                "credit_limit": Decimal("40000"),
            }
        )

    reservations = ReservationService(session)
    customer = customers.repo.list()[0]
    if not reservations.repo.list() and asset_ids:
        start = utcnow() + timedelta(days=1)
        reservations.create(
            {
                "customer_id": customer.id,
                "starts_at": start,
                "ends_at": start + timedelta(days=3),
                "notes": "demo reservation",
                "lines": [{"asset_id": asset_ids[0]}, {"asset_id": asset_ids[1]}],
            }
        )

    return {
        "categories": len(cat_by_name),
        "assets": len(asset_ids),
        "customers": len(customers.repo.list()),
    }
