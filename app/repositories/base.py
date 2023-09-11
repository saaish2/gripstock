"""Generic repository base class.

Repositories own all query construction so services never touch the ORM
session directly with raw SQLAlchemy expressions. This keeps data-access
concerns — soft deletes, ordering defaults, eager loads — in one place.
"""

from __future__ import annotations

from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.base import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    model: type[ModelT]

    def __init__(self, session: Session) -> None:
        self.session = session
