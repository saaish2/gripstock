"""FastAPI application factory."""

from __future__ import annotations

from fastapi import FastAPI

from app import __version__
from app.config import get_settings
from app.errors import register_error_handlers
from app.logging import configure_logging
from app.middleware import RequestContextMiddleware
from app.routers import api_router
