"""API tests for the quoting endpoint."""

from __future__ import annotations

from datetime import datetime, timedelta


def _window():
    start = datetime(2025, 4, 1, 9, 0)
    return start.isoformat(), (start + timedelta(days=3)).isoformat()
