"""Unit tests for security primitives."""

from __future__ import annotations

from app.security import (
    constant_time_equals,
    fingerprint_token,
    generate_api_key,
    generate_token,
    hash_password,
    verify_password,
)


def test_password_hash_roundtrip():
    hashed = hash_password("hunter2-ok")
    assert hashed != "hunter2-ok"
    assert verify_password("hunter2-ok", hashed)
    assert not verify_password("wrong", hashed)
