"""Domain error hierarchy and FastAPI exception handlers.

Services raise these typed errors instead of HTTP exceptions so the business
layer stays framework-agnostic. A thin translation layer maps each error class
to an HTTP status and a structured JSON envelope.
"""

from __future__ import annotations

from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse


class GripstockError(Exception):
    """Base class for every error the domain raises."""

    status_code: int = 500
    code: str = "internal_error"

    def __init__(self, message: str, *, details: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.details = details or {}

    def to_payload(self) -> dict[str, Any]:
        body: dict[str, Any] = {"error": {"code": self.code, "message": self.message}}
        if self.details:
            body["error"]["details"] = self.details
        return body


class ValidationError(GripstockError):
    status_code = 422
    code = "validation_error"


class NotFoundError(GripstockError):
    status_code = 404
    code = "not_found"


class ConflictError(GripstockError):
    status_code = 409
    code = "conflict"


class AuthenticationError(GripstockError):
    status_code = 401
    code = "unauthenticated"


class PermissionDeniedError(GripstockError):
    status_code = 403
    code = "permission_denied"


class InvalidStateError(GripstockError):
    """Raised when an entity cannot transition to the requested state."""

    status_code = 409
    code = "invalid_state"


class BusinessRuleError(GripstockError):
    """Raised when a domain invariant would be violated."""

    status_code = 422
    code = "business_rule_violation"


class RateLimitedError(GripstockError):
