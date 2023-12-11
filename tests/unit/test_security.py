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


def test_verify_rejects_garbage_hash():
    assert not verify_password("anything", "not-a-real-hash")


def test_generate_token_is_unique():
    assert generate_token() != generate_token()
