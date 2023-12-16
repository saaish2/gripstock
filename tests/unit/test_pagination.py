"""Unit tests for pagination helpers."""

from __future__ import annotations

from app.pagination import DEFAULT_PAGE_SIZE, MAX_PAGE_SIZE, Page, PageParams


def test_page_params_clamps():
    assert PageParams(page=0).page == 1
    assert PageParams(size=0).size == DEFAULT_PAGE_SIZE
    assert PageParams(size=9999).size == MAX_PAGE_SIZE


def test_page_params_offset():
    assert PageParams(page=1, size=25).offset == 0
    assert PageParams(page=3, size=10).offset == 20


def test_page_metadata():
    page = Page(items=[1, 2, 3], total=23, page=2, size=10)
    assert page.pages == 3
    assert page.has_next is True
    assert page.has_prev is True


def test_page_first_and_last():
    first = Page(items=[], total=5, page=1, size=10)
    assert first.has_prev is False
    assert first.has_next is False
    assert first.pages == 1


def test_page_to_dict():
    page = Page(items=[{"id": 1}], total=1, page=1, size=10)
    out = page.to_dict(lambda x: x)
    assert out["items"] == [{"id": 1}]
    assert out["pagination"]["total"] == 1
