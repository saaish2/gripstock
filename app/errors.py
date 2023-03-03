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
