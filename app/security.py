"""Password hashing, token generation, and constant-time comparisons."""

from __future__ import annotations

import hashlib
import hmac
import secrets

# PBKDF2-HMAC-SHA256 password hashing. Stdlib-only so the service has no
# native-extension dependency, and deterministic given salt + iterations,
# which keeps the auth tests fast and reproducible.
_ALGORITHM = "pbkdf2_sha256"
_ITERATIONS = 180_000
_SALT_BYTES = 16


def hash_password(password: str) -> str:
    """Return a salted PBKDF2 hash encoded as ``algo$iters$salt$digest``."""

    salt = secrets.token_bytes(_SALT_BYTES)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, _ITERATIONS)
    return f"{_ALGORITHM}${_ITERATIONS}${salt.hex()}${digest.hex()}"


def verify_password(password: str, hashed: str) -> bool:
    """Check ``password`` against a previously stored hash."""

    try:
        algorithm, iterations, salt_hex, digest_hex = hashed.split("$")
        if algorithm != _ALGORITHM:
            return False
        expected = bytes.fromhex(digest_hex)
        candidate = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), bytes.fromhex(salt_hex), int(iterations)
        )
        return hmac.compare_digest(expected, candidate)
    except (ValueError, AttributeError):
        return False
