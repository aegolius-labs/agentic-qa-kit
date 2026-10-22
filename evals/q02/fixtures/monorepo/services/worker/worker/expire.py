"""Expire unpaid booking holds older than the hold window."""

from __future__ import annotations

from datetime import datetime, timedelta

HOLD_WINDOW = timedelta(minutes=15)


def expired(holds: list[dict], now: datetime) -> list[str]:
    """IDs of unpaid holds created at least HOLD_WINDOW before now."""

    return [
        hold["id"]
        for hold in holds
        if not hold.get("paid") and now - hold["created_at"] >= HOLD_WINDOW
    ]
