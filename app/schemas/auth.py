"""Auth and user schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

from app.enums import Role
from app.schemas.common import ORMModel


class LoginRequest(BaseModel):
    email: EmailStr
