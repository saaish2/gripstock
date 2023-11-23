"""Shared pytest fixtures.

Every test runs against a throwaway file-backed SQLite database so foreign
keys behave like production. The engine is rebuilt per test for isolation.
"""

from __future__ import annotations

import os
import tempfile
from collections.abc import Iterator
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
