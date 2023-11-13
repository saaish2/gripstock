"""FastAPI application factory."""

from __future__ import annotations

from fastapi import FastAPI

from app import __version__
from app.config import get_settings
from app.errors import register_error_handlers
from app.logging import configure_logging
from app.middleware import RequestContextMiddleware
from app.routers import api_router


def create_app() -> FastAPI:
    settings = get_settings()
    configure_logging(settings.log_level, settings.log_json)

    app = FastAPI(
        title="Gripstock",
        version=__version__,
        description="Equipment-rental operations platform for production rental houses.",
        docs_url="/docs",
        redoc_url="/redoc",
    )
    app.add_middleware(RequestContextMiddleware)
    register_error_handlers(app)
    app.include_router(api_router)

    @app.get("/", tags=["health"])
    def root() -> dict:
        return {"service": "gripstock", "version": __version__, "docs": "/docs"}

    return app
