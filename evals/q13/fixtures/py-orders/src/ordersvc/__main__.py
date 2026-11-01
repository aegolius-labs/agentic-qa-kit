"""Command line entry point."""

from __future__ import annotations

import argparse
import json
import sys

from .service import Metrics, OrderFailed, place_order


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ordersvc")
    parser.add_argument("order", help="JSON file with order_id, sku and card")
    parser.add_argument("--metrics", action="store_true", help="print counters after the result")
    args = parser.parse_args(argv)
    with open(args.order, encoding="utf-8") as handle:
        order = json.load(handle)
    metrics = Metrics()
    status = 0
    try:
        result = place_order(order["order_id"], order["sku"], order["card"], metrics)
    except OrderFailed as error:
        result = {"order_id": order["order_id"], "status": "failed", "error": str(error)}
        status = 1
    print(json.dumps(result))
    if args.metrics:
        print(json.dumps(metrics.counters, sort_keys=True))
    return status


if __name__ == "__main__":
    sys.exit(main())
