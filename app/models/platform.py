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
    fingerprint: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    prefix: Mapped[str] = mapped_column(String(12), nullable=False)
    scopes: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    created_by_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    @property
    def is_active(self) -> bool:
        return self.revoked_at is None

    def scope_list(self) -> list[str]:
        return [s for s in self.scopes.split(",") if s]


class WebhookEndpoint(Base, IntPrimaryKey, TimestampMixin):
    __tablename__ = "webhook_endpoints"

    url: Mapped[str] = mapped_column(String(500), nullable=False)
    secret: Mapped[str] = mapped_column(String(120), nullable=False)
    event_types: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    deliveries: Mapped[list[WebhookDelivery]] = relationship(
        back_populates="endpoint", cascade="all, delete-orphan"
    )

    def subscribes_to(self, event_type: str) -> bool:
        types = {t for t in self.event_types.split(",") if t}
        return "*" in types or event_type in types


class WebhookDelivery(Base, IntPrimaryKey, TimestampMixin):
    __tablename__ = "webhook_deliveries"

    endpoint_id: Mapped[int] = mapped_column(
        ForeignKey("webhook_endpoints.id", ondelete="CASCADE"), index=True, nullable=False
    )
    event_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    payload: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[WebhookStatus] = mapped_column(
        String(20), default=WebhookStatus.PENDING, index=True, nullable=False
    )
    attempts: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    next_attempt_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), index=True, nullable=True
    )
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)
    delivered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    endpoint: Mapped[WebhookEndpoint] = relationship(back_populates="deliveries")


class IdempotencyKey(Base, IntPrimaryKey):
    __tablename__ = "idempotency_keys"

    key: Mapped[str] = mapped_column(String(120), unique=True, index=True, nullable=False)
