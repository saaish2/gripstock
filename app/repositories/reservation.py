"""Reservation repository with overlap-detection queries."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import Select, and_, select

from app.enums import ReservationStatus
from app.models.reservation import Reservation, ReservationLine
from app.repositories.base import BaseRepository
