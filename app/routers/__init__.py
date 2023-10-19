"""API router assembly."""

from __future__ import annotations

from fastapi import APIRouter

from app.routers import (
    apikeys,
    assets,
    audit,
    auth,
    categories,
    customers,
    health,
    invoices,
    kits,
    operations,
    orders,
    quotes,
    reports,
    reservations,
    users,
    webhooks,
)

api_router = APIRouter()
