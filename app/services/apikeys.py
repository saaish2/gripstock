"""API-key lifecycle service."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.errors import AuthenticationError, NotFoundError
from app.models.base import utcnow
from app.models.platform import ApiKey
from app.repositories.operations import ApiKeyRepository
from app.security import fingerprint_token, generate_api_key


class ApiKeyService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.repo = ApiKeyRepository(session)

    def issue(self, label: str, scopes: list[str], created_by_id: int | None = None) -> tuple[ApiKey, str]:
        plaintext, fingerprint = generate_api_key()
        key = ApiKey(
            label=label,
            fingerprint=fingerprint,
            prefix=plaintext[:8],
            scopes=",".join(scopes),
            created_by_id=created_by_id,
        )
        self.repo.add(key)
        return key, plaintext

    def authenticate(self, plaintext: str) -> ApiKey:
        key = self.repo.get_by_fingerprint(fingerprint_token(plaintext))
        if key is None or not key.is_active:
            raise AuthenticationError("invalid or revoked API key")
        key.last_used_at = utcnow()
        self.session.flush()
        return key
