"""Cursor-free offset pagination helpers shared by every list endpoint."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

T = TypeVar("T")

MAX_PAGE_SIZE = 100
DEFAULT_PAGE_SIZE = 25


@dataclass(slots=True)
class PageParams:
    """Validated pagination inputs."""

    page: int = 1
    size: int = DEFAULT_PAGE_SIZE

    def __post_init__(self) -> None:
        if self.page < 1:
            self.page = 1
        if self.size < 1:
            self.size = DEFAULT_PAGE_SIZE
        if self.size > MAX_PAGE_SIZE:
            self.size = MAX_PAGE_SIZE

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.size


@dataclass(slots=True)
class Page(Generic[T]):
    """A single page of results plus enough metadata to render controls."""

    items: list[T]
    total: int
    page: int
    size: int

    @property
    def pages(self) -> int:
        if self.size == 0:
            return 0
        return (self.total + self.size - 1) // self.size

    @property
    def has_next(self) -> bool:
        return self.page < self.pages

    @property
    def has_prev(self) -> bool:
        return self.page > 1

    def to_dict(self, serializer) -> dict:  # noqa: ANN001
        return {
            "items": [serializer(item) for item in self.items],
            "pagination": {
                "page": self.page,
                "size": self.size,
                "total": self.total,
                "pages": self.pages,
                "has_next": self.has_next,
                "has_prev": self.has_prev,
            },
        }
