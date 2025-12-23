"""End-to-end API test of the full rental lifecycle."""

from __future__ import annotations

from datetime import datetime, timedelta


def _window(days_ahead=1, length=3):
    start = datetime(2025, 5, 1, 9, 0) + timedelta(days=days_ahead)
    end = start + timedelta(days=length)
    return start.isoformat(), end.isoformat()
