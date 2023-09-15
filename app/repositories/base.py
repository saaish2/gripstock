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

    def add(self, entity: ModelT) -> ModelT:
        self.session.add(entity)
        self.session.flush()
        return entity

    def get(self, entity_id: int) -> ModelT | None:
        return self.session.get(self.model, entity_id)

    def list(self) -> list[ModelT]:
        return list(self.session.execute(select(self.model)).scalars().all())

    def delete(self, entity: ModelT) -> None:
        self.session.delete(entity)
        self.session.flush()

    def count(self) -> int:
        from sqlalchemy import func

        stmt = select(func.count()).select_from(self.model)
        return self.session.execute(stmt).scalar_one()

    def exists(self, entity_id: int) -> bool:
        return self.get(entity_id) is not None
