"""Place an order: reserve stock, then charge the card."""

from __future__ import annotations

import json
import sys
import uuid
from datetime import datetime, timezone
from typing import Any, TextIO

from . import backends

PRICE_CENTS = 1999


class OrderFailed(Exception):
    pass


class Metrics:
    def __init__(self) -> None:
        self.counters: dict[str, int] = {}

    def inc(self, name: str, **labels: str) -> None:
        key = name + "".join(f'{{{k}="{v}"}}' for k, v in sorted(labels.items()))
        self.counters[key] = self.counters.get(key, 0) + 1


def _log(stream: TextIO, level: str, event: str, **fields: Any) -> None:
    line = {"ts": datetime.now(timezone.utc).isoformat(), "level": level, "event": event, **fields}
    stream.write(json.dumps(line) + "\n")


def place_order(order_id: str, sku: str, card: str, metrics: Metrics, log: TextIO = sys.stderr) -> dict[str, Any]:
    request_id = uuid.uuid4().hex[:12]
    ids = {"request_id": request_id, "order_id": order_id}
    _log(log, "info", "order_received", sku=sku, **ids)
    try:
        try:
            backends.reserve(sku)
        except backends.OutOfStock:
            _log(log, "error", "inventory_unavailable", reason="out_of_stock", **ids)
            metrics.inc("orders_failed_total", reason="out_of_stock")
            raise OrderFailed("out_of_stock")
        try:
            charge_id = backends.charge(card, PRICE_CENTS)
        except backends.Declined as error:
            _log(log, "error", "payment_declined", reason=error.code, card=card, **ids)
            metrics.inc("orders_failed_total", reason=error.code)
            raise OrderFailed(error.code)
    except OrderFailed:
        raise
    except Exception:
        _log(log, "error", "order_failed", msg="failed")
        metrics.inc("orders_failed_total", reason="unknown")
        raise OrderFailed("unknown")
    _log(log, "info", "order_placed", charge_id=charge_id, card_last4=card[-4:], **ids)
    metrics.inc("orders_placed_total")
    return {"order_id": order_id, "status": "placed", "charge_id": charge_id}
