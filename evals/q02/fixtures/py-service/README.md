# orders-api

Read-only JSON API over the orders database.

- `GET /orders?page=N&size=M` returns orders sorted by id, `size` per page
  (default 20, at most 100), pages counted from 1.
- `GET /healthz` returns `{"ok": true}`.

## Running

The service needs PostgreSQL. Start it with `docker compose up -d db`, then:

```bash
export DATABASE_URL=postgresql://orders:orders@localhost:5432/orders
python -m app.server --port 8080
```

## Tests

```bash
python -m unittest discover -s tests            # unit tests, no database
DATABASE_URL=... python -m unittest discover -s tests/integration
```
