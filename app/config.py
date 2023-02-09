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
