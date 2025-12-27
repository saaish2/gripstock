"""API tests for RBAC enforcement and idempotent order creation."""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from app.database import session_scope
from app.enums import Role
from app.services.auth import AuthService
