"""Quote endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import db_session, require_agent
from app.models.user import User
from app.schemas.quote import QuoteOut, QuoteRequest
from app.services.quotes import QuoteService

router = APIRouter(prefix="/quotes", tags=["quotes"])
