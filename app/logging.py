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
