"""Application configuration loaded from the environment.

Settings are read once at startup and cached. Every knob carries a sane
default so the service boots with zero configuration in development, while
production overrides everything through ``GRIPSTOCK_*`` environment variables.
"""

from __future__ import annotations

from decimal import Decimal
from functools import lru_cache
from typing import Literal

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

Environment = Literal["development", "test", "staging", "production"]


class Settings(BaseSettings):
    """Strongly-typed view over the process environment."""

    model_config = SettingsConfigDict(
        env_prefix="GRIPSTOCK_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    env: Environment = "development"
    debug: bool = True
    secret_key: str = "dev-insecure-secret-key"

    database_url: str = "sqlite:///./gripstock.db"
    database_echo: bool = False

    session_ttl_minutes: int = 720
    password_min_length: int = 10

    default_deposit_rate: Decimal = Decimal("0.20")
    late_fee_daily_rate: Decimal = Decimal("0.05")
    grace_period_hours: int = 4
    weekly_tier_days: int = 7
    monthly_tier_days: int = 28

    webhook_max_attempts: int = 5
    webhook_backoff_seconds: int = 30

    log_level: str = "INFO"
    log_json: bool = False

    @field_validator("default_deposit_rate", "late_fee_daily_rate")
    @classmethod
    def _non_negative_rate(cls, value: Decimal) -> Decimal:
        if value < 0:
            raise ValueError("rate must not be negative")
        return value

    @field_validator("password_min_length")
    @classmethod
    def _sane_password_length(cls, value: int) -> int:
        if value < 6:
            raise ValueError("password_min_length must be at least 6")
        return value

    @property
    def is_production(self) -> bool:
        return self.env == "production"

    @property
    def is_testing(self) -> bool:
        return self.env == "test"

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


@lru_cache
def get_settings() -> Settings:
    """Return the process-wide settings singleton."""

    return Settings()
