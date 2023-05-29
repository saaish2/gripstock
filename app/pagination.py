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
