"""Declarative base and reusable column mixins."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


def utcnow() -> datetime:
    """Return a naive UTC timestamp.

    We deliberately drop the tzinfo: SQLite does not preserve timezone on
    round-trip, so storing aware values would make persisted timestamps
    uncomparable with freshly-minted ones. Treating every stored timestamp as
    UTC-naive keeps comparisons consistent across SQLite and PostgreSQL.
    """

    return datetime.now(UTC).replace(tzinfo=None)


class Base(DeclarativeBase):
    """Project-wide declarative base."""

    pass


class IntPrimaryKey:
    """Mixin adding an autoincrement integer primary key."""

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
