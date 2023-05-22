"""Cursor-free offset pagination helpers shared by every list endpoint."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Generic, TypeVar

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session
