"""API tests for health and authentication."""

from __future__ import annotations


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_root(client):
    resp = client.get("/")
    assert resp.status_code == 200
    assert resp.json()["service"] == "gripstock"


def test_login_and_me(client, auth_headers):
    resp = client.get("/auth/me", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["email"] == "admin@test.com"


def test_login_rejects_bad_password(client, admin_token):
    resp = client.post(
        "/auth/login",
        json={"email": "admin@test.com", "password": "wrong"},
    )
    assert resp.status_code == 401


def test_protected_route_requires_token(client):
    resp = client.get("/auth/me")
    assert resp.status_code == 401


def test_logout_revokes_session(client, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    assert client.post("/auth/logout", headers=headers).status_code == 200
    assert client.get("/auth/me", headers=headers).status_code == 401
