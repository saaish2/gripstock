"""Unit tests for pagination helpers."""

from __future__ import annotations

from app.pagination import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, Page, PageParams


def test_page_params_clamps():
    assert PageParams(page=0).page == 1
    assert PageParams(size=0).size == DEFAULT_PAGE_SIZE
    assert PageParams(size=9999).size == MAX_PAGE_SIZE
