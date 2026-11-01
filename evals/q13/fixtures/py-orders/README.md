# ordersvc

Places an order: reserves stock, then charges the card. An order is a JSON
file with `order_id`, `sku` and `card`; `samples/` has one.

```bash
PYTHONPATH=src python -m ordersvc samples/order-a1001.json
```

It prints the order result as JSON on stdout, writes one JSON log line per
event to stderr, and with `--metrics` prints its counters to stdout after the
result.

The inventory and payment backends are local fakes. Choose their behavior
with environment variables:

| Variable | Values | Default |
| --- | --- | --- |
| `ORDERSVC_FAKE_INVENTORY` | `ok`, `out_of_stock`, `timeout` | `ok` |
| `ORDERSVC_FAKE_PAYMENT` | `ok`, `declined` | `ok` |

The logging and metrics contract is in [docs/observability.md](docs/observability.md).

Run the tests with:

```bash
PYTHONPATH=src python -m unittest discover -s tests
```
