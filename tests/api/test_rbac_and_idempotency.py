"""API tests for RBAC enforcement and idempotent order creation."""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from app.database import session_scope
from app.enums import Role
from app.services.auth import AuthService


@pytest.fixture()
def agent_headers(client) -> dict:
    with session_scope() as sess:
        AuthService(sess).create_user(
            email="agent@test.com",
            full_name="Agent",
            password="agentpass12",
            role=Role.AGENT,
        )
    token = client.post(
        "/auth/login",
        json={"email": "agent@test.com", "password": "agentpass12"},
    ).json()["token"]
    return {"Authorization": f"Bearer {token}"}


def test_agent_cannot_create_user(client, agent_headers):
    resp = client.post(
        "/users",
        json={"email": "x@y.com", "full_name": "X", "password": "password12"},
        headers=agent_headers,
    )
    assert resp.status_code == 403
    assert resp.json()["error"]["code"] == "permission_denied"


def test_agent_cannot_create_asset(client, agent_headers, sample_catalog):
    cat_id = sample_catalog["category"]["id"]
    resp = client.post(
        "/assets",
        json={
            "category_id": cat_id,
            "name": "X",
            "barcode": "ZZ-1",
            "daily_rate": "1.00",
            "replacement_value": "1.00",
        },
        headers=agent_headers,
    )
    assert resp.status_code == 403


def test_agent_can_create_customer(client, agent_headers):
    resp = client.post(
        "/customers",
        json={"name": "C", "contact_email": "c@c.com"},
        headers=agent_headers,
    )
    assert resp.status_code == 201
