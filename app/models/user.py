"""User and session ORM models."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.enums import Role
from app.models.base import Base, IntPrimaryKey, TimestampMixin
