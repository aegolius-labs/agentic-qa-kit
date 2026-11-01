# Observability contract

On-call engineers diagnose failed orders from logs and metrics alone. Every
release must keep this contract.

## Logs

- One JSON object per line on stderr.
- Every line has `ts`, `level`, `event`, `request_id` and `order_id`.
- A failed order logs exactly one `level: "error"` line whose `event` names
  the failing step and whose `reason` names the cause:

| Step | `event` | `reason` values |
| --- | --- | --- |
| Inventory | `inventory_unavailable` | `out_of_stock`, `timeout` |
| Payment | `payment_declined` | the processor's decline code |

- Card numbers are never logged. Log `card_last4` only.

## Metrics

- `orders_placed_total` counts placed orders.
- `orders_failed_total{reason}` counts failed orders. Its `reason` label is
  the same value as the error log line's `reason`.

## Production

Production logs and dashboards are in the shared log store at
https://logs.example.internal/ordersvc. Querying it needs approval from the
on-call lead.
