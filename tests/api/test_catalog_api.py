"""API tests for catalog endpoints."""

from __future__ import annotations


def test_create_and_get_asset(client, auth_headers, sample_catalog):
    asset_id = sample_catalog["asset_a"]["id"]
    resp = client.get(f"/assets/{asset_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["barcode"] == "CAM-001"
