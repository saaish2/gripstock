"""API tests for catalog endpoints."""

from __future__ import annotations


def test_create_and_get_asset(client, auth_headers, sample_catalog):
    asset_id = sample_catalog["asset_a"]["id"]
    resp = client.get(f"/assets/{asset_id}", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["barcode"] == "CAM-001"


def test_list_assets_paginated(client, auth_headers, sample_catalog):
    resp = client.get("/assets?size=1", headers=auth_headers)
    assert resp.status_code == 200
    body = resp.json()
    assert body["pagination"]["size"] == 1
    assert body["pagination"]["total"] >= 2
    assert len(body["items"]) == 1


def test_search_assets_by_term(client, auth_headers, sample_catalog):
    resp = client.get("/assets?term=komodo", headers=auth_headers)
    assert resp.status_code == 200
    names = [a["name"] for a in resp.json()["items"]]
    assert "Komodo" in names


def test_duplicate_barcode_conflict(client, auth_headers, sample_catalog):
    cat_id = sample_catalog["category"]["id"]
    resp = client.post(
        "/assets",
        json={
            "category_id": cat_id,
            "name": "Dup",
            "barcode": "CAM-001",
            "daily_rate": "10.00",
            "replacement_value": "100.00",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 409
    assert resp.json()["error"]["code"] == "conflict"


def test_asset_status_transition_via_api(client, auth_headers, sample_catalog):
    asset_id = sample_catalog["asset_b"]["id"]
    resp = client.post(
        f"/assets/{asset_id}/status",
        json={"status": "in_maintenance"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "in_maintenance"
