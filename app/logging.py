"""Structured logging setup.

The platform emits either human-friendly lines (development) or single-line
JSON records (production) so log aggregation stays trivial. A request-id
context variable is threaded through so every log line within a request can be
correlated after the fact.
"""

from __future__ import annotations

import json
import logging
import sys
from contextvars import ContextVar
from typing import Any

_request_id: ContextVar[str | None] = ContextVar("request_id", default=None)


def set_request_id(value: str | None) -> None:
    _request_id.set(value)


def get_request_id() -> str | None:
    return _request_id.get()
