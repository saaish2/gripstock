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
api_router.include_router(operations.router)
# Maintenance endpoints are defined alongside operations but mounted separately.
api_router.include_router(operations.maintenance_router)
api_router.include_router(webhooks.router)
api_router.include_router(apikeys.router)
api_router.include_router(reports.router)
