"""API-key lifecycle service."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.errors import AuthenticationError, NotFoundError
from app.models.base import utcnow
from app.models.platform import ApiKey
from app.repositories.operations import ApiKeyRepository
from app.security import fingerprint_token, generate_api_key
