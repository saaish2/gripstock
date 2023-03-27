"""Database engine, session factory, and unit-of-work helpers."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from app.config import Settings, get_settings

_engine: Engine | None = None
_SessionFactory: sessionmaker[Session] | None = None


def _build_engine(settings: Settings) -> Engine:
    connect_args: dict[str, object] = {}
    if settings.is_sqlite:
        connect_args["check_same_thread"] = False
    engine = create_engine(
        settings.database_url,
        echo=settings.database_echo,
        connect_args=connect_args,
        future=True,
    )
    if settings.is_sqlite:
        _enable_sqlite_foreign_keys(engine)
    return engine


def _enable_sqlite_foreign_keys(engine: Engine) -> None:
    @event.listens_for(engine, "connect")
    def _set_pragma(dbapi_connection, _record):  # noqa: ANN001
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


def get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = _build_engine(get_settings())
    return _engine


def get_session_factory() -> sessionmaker[Session]:
    global _SessionFactory
    if _SessionFactory is None:
        _SessionFactory = sessionmaker(
            bind=get_engine(), autoflush=False, expire_on_commit=False, future=True
        )
    return _SessionFactory
