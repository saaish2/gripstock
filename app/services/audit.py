"""Audit-log helper used by every mutating service."""

from __future__ import annotations

import json
from typing import Any

from sqlalchemy.orm import Session

from app.models.base import utcnow
from app.models.platform import AuditLog
