"""API tests for the quoting endpoint."""

from __future__ import annotations

from datetime import datetime, timedelta


def _window():
    start = datetime(2025, 4, 1, 9, 0)
    return start.isoformat(), (start + timedelta(days=3)).isoformat()


def test_quote_two_assets(client, auth_headers, sample_catalog):
    starts_at, ends_at = _window()
    resp = client.post(
        "/quotes",
        json={
            "starts_at": starts_at,
            "ends_at": ends_at,
            "asset_ids": [sample_catalog["asset_a"]["id"], sample_catalog["asset_b"]["id"]],
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["rental_days"] == 3
    assert len(body["lines"]) == 2
    # asset_a 650/day * 3 = 1950; asset_b 450/day * 3 = 1350; total 3300.
    assert body["subtotal"] == "3300.00"


def test_quote_applies_customer_discount(client, auth_headers, sample_catalog, sample_customer):
    starts_at, ends_at = _window()
    resp = client.post(
        "/quotes",
        json={
            "customer_id": sample_customer["id"],
            "starts_at": starts_at,
            "ends_at": ends_at,
            "asset_ids": [sample_catalog["asset_a"]["id"]],
        },
        headers=auth_headers,
    )
    body = resp.json()
    # 5% customer discount on 1950 = 97.50.
    assert body["discount_total"] == "97.50"
    assert body["net_total"] == "1852.50"
