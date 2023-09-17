"""User and session repositories."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import select

from app.models.user import Session as SessionModel
from app.models.user import User
from app.repositories.base import BaseRepository
