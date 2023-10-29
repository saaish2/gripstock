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
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(customers.router)
api_router.include_router(categories.router)
api_router.include_router(assets.router)
api_router.include_router(kits.router)
api_router.include_router(reservations.router)
api_router.include_router(orders.router)
api_router.include_router(quotes.router)
api_router.include_router(invoices.router)
