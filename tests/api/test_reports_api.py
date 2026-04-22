"""API tests for reporting endpoints."""

from __future__ import annotations


def test_dashboard(client, auth_headers, sample_catalog):
    resp = client.get("/reports/dashboard", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert "inventory" in body
    assert "revenue" in body
    assert body["inventory"]["total"] >= 2


def test_inventory_report(client, auth_headers, sample_catalog):
    resp = client.get("/reports/inventory", headers=auth_headers)
    assert resp.status_code == 200
    assert "by_status" in resp.json()
