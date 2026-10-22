"""Pagination arithmetic, kept free of I/O so it can be unit tested."""

from __future__ import annotations

DEFAULT_SIZE = 20
MAX_SIZE = 100


def parse(query: dict[str, list[str]]) -> tuple[int, int]:
    """Return (page, size) from a parsed query string, applying the limits."""

    page = int(query.get("page", ["1"])[0])
    size = int(query.get("size", [str(DEFAULT_SIZE)])[0])
    if page < 1:
        raise ValueError("page must be at least 1")
    if size < 1:
        raise ValueError("size must be at least 1")
    return page, min(size, MAX_SIZE)


def window(page: int, size: int) -> tuple[int, int]:
    """SQL (limit, offset) for a 1-based page."""

    return size, page * size - size + (1 if page > 1 else 0)
