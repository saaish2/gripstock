"""ASGI entry point.

Run with ``uvicorn app.main:app --reload`` in development.
"""

from __future__ import annotations

from app.factory import create_app

app = create_app()
