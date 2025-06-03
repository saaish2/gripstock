"""Quote endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.deps import db_session, require_agent
from app.models.user import User
from app.schemas.quote import QuoteOut, QuoteRequest
from app.services.quotes import QuoteService

router = APIRouter(prefix="/quotes", tags=["quotes"])


@router.post("", response_model=QuoteOut)
def create_quote(
    payload: QuoteRequest,
    _: User = Depends(require_agent),
    session: Session = Depends(db_session),
) -> QuoteOut:
    result = QuoteService(session).quote(
        payload.asset_ids,
        payload.starts_at,
        payload.ends_at,
        customer_id=payload.customer_id,
        bundle_discount=payload.bundle_discount,
    )
    return QuoteOut.model_validate(result)
