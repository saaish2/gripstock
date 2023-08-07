"""Shared schema primitives."""

from __future__ import annotations

from datetime import datetime
from typing import Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ORMModel(BaseModel):
    """Base for schemas that read from ORM objects."""

    model_config = ConfigDict(from_attributes=True)


class PaginationMeta(BaseModel):
    page: int
    size: int
    total: int
