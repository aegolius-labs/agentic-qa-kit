"""Local fake backends, selected by environment variables."""

from __future__ import annotations

import os


class OutOfStock(Exception):
    pass


class Declined(Exception):
    def __init__(self, code: str) -> None:
        super().__init__(code)
        self.code = code


def reserve(sku: str) -> None:
    mode = os.environ.get("ORDERSVC_FAKE_INVENTORY", "ok")
    if mode == "out_of_stock":
        raise OutOfStock(sku)
    if mode == "timeout":
        raise TimeoutError(f"inventory did not answer for {sku}")


def charge(card: str, amount_cents: int) -> str:
    if os.environ.get("ORDERSVC_FAKE_PAYMENT", "ok") == "declined":
        raise Declined("insufficient_funds")
    return "ch_" + card[-4:]
