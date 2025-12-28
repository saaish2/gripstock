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
