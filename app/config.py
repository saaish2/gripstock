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
