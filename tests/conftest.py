"""Shared pytest fixtures.

Every test runs against a throwaway file-backed SQLite database so foreign
keys behave like production. The engine is rebuilt per test for isolation.
"""

from __future__ import annotations

import os
import tempfile
from collections.abc import Iterator
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

os.environ.setdefault("GRIPSTOCK_ENV", "test")
os.environ.setdefault("GRIPSTOCK_SECRET_KEY", "test-secret")

from app.config import reset_settings_cache  # noqa: E402
from app.database import get_session_factory, reset_engine  # noqa: E402
from app.enums import Role  # noqa: E402
from app.factory import create_app  # noqa: E402


@pytest.fixture()
def db_path() -> Iterator[str]:
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    try:
        os.remove(path)
    except OSError:
        pass


@pytest.fixture()
def configured_env(db_path: str) -> Iterator[None]:
    os.environ["GRIPSTOCK_DATABASE_URL"] = f"sqlite:///{db_path}"
    reset_settings_cache()
    reset_engine()
    from app.bootstrap import create_all

    create_all()
    yield
    reset_engine()


@pytest.fixture()
def session(configured_env: None) -> Iterator[Session]:
    factory = get_session_factory()
    sess = factory()
    try:
        yield sess
        sess.commit()
    finally:
        sess.close()


@pytest.fixture()
def client(configured_env: None) -> Iterator[TestClient]:
    app = create_app()
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture()
def admin_token(client: TestClient) -> str:
    from app.database import session_scope
    from app.services.auth import AuthService

    with session_scope() as sess:
        AuthService(sess).create_user(
            email="admin@test.com",
            full_name="Admin",
            password="supersecret1",
            role=Role.ADMIN,
        )
    resp = client.post(
        "/auth/login",
        json={"email": "admin@test.com", "password": "supersecret1"},
    )
    assert resp.status_code == 200, resp.text
    return resp.json()["token"]


@pytest.fixture()
def auth_headers(admin_token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {admin_token}"}
