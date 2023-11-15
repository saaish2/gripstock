"""Schema bootstrap helpers.

For local development and tests we create tables directly from the ORM
metadata. Production uses Alembic migrations (see ``migrations/``).
"""

from __future__ import annotations

from sqlalchemy.engine import Engine

from app.database import get_engine
from app.models import Base


def create_all(engine: Engine | None = None) -> None:
    Base.metadata.create_all(bind=engine or get_engine())
