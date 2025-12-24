"""End-to-end API test of the full rental lifecycle."""

from __future__ import annotations

from datetime import datetime, timedelta


def _window(days_ahead=1, length=3):
    start = datetime(2025, 5, 1, 9, 0) + timedelta(days=days_ahead)
    end = start + timedelta(days=length)
    return start.isoformat(), end.isoformat()


def _reservation(client, headers, customer_id, asset_ids):
    starts_at, ends_at = _window()
    return client.post(
        "/reservations",
        json={
            "customer_id": customer_id,
            "starts_at": starts_at,
            "ends_at": ends_at,
            "lines": [{"asset_id": aid} for aid in asset_ids],
        },
        headers=headers,
    )
