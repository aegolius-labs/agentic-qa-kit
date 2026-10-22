"""Minimal orders API. Needs DATABASE_URL and the psycopg driver."""

from __future__ import annotations

import argparse
import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlparse

from . import paging


def fetch_orders(limit: int, offset: int) -> list[dict]:
    import psycopg  # imported lazily: unit tests never reach the database

    with psycopg.connect(os.environ["DATABASE_URL"]) as conn:
        rows = conn.execute(
            "SELECT id, customer, total_cents FROM orders ORDER BY id LIMIT %s OFFSET %s",
            (limit, offset),
        ).fetchall()
    return [{"id": r[0], "customer": r[1], "total_cents": r[2]} for r in rows]


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        url = urlparse(self.path)
        if url.path == "/healthz":
            return self._send(200, {"ok": True})
        if url.path == "/orders":
            try:
                page, size = paging.parse(parse_qs(url.query))
            except ValueError as exc:
                return self._send(400, {"error": str(exc)})
            limit, offset = paging.window(page, size)
            return self._send(200, {"page": page, "orders": fetch_orders(limit, offset)})
        self._send(404, {"error": "not found"})

    def _send(self, status: int, body: dict) -> None:
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
