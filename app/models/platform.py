"""Platform-support ORM models: audit log, API keys, webhooks, idempotency."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.enums import WebhookStatus
from app.models.base import Base, IntPrimaryKey, TimestampMixin


class AuditLog(Base, IntPrimaryKey):
    __tablename__ = "audit_logs"

    actor_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), index=True, nullable=True
    )
    action: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    entity_type: Mapped[str] = mapped_column(String(60), index=True, nullable=False)
    entity_id: Mapped[str] = mapped_column(String(60), index=True, nullable=False)
    payload: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), index=True, nullable=False
    )


class ApiKey(Base, IntPrimaryKey, TimestampMixin):
    __tablename__ = "api_keys"

    label: Mapped[str] = mapped_column(String(120), nullable=False)
