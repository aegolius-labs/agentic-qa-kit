# helpdesk

A support agent that handles refund tickets: it looks up the order, issues the
refund and emails the customer. Its rules are in
[docs/agent-policy.md](docs/agent-policy.md).

```bash
PYTHONPATH=src python -m helpdesk reset
PYTHONPATH=src python -m helpdesk run --task tasks/refund-1042.json --seed 7
PYTHONPATH=src python -m helpdesk run --task tasks/refund-1043.json --seed 7 --stop-after 2
```

The agent's model is chosen with `HELPDESK_MODEL`:

- `stub` (the default) is a local, seeded stand-in for the model. The same
  seed gives the same run. It costs nothing.
- `hosted` calls the hosted model at https://api.model-provider.example, billed
  per token to the team account, and needs `HELPDESK_API_KEY`.

The agent's tools act on a sandbox in `.sandbox/`: `orders.json`, the email
`outbox.jsonl`, `handoffs.jsonl`, a `tool-calls.jsonl` log and `usage.json`. `reset` restores it
from `seed-data/`. `run` refuses to start without a sandbox and does not reset
it. `--fault email-timeout` makes the first email send time out.

`python -m helpdesk stop` is the operator's stop: it tells a running agent to
stop. `run --stop-after N` sends that stop after the agent's Nth tool call, so
a stop can land at a chosen point of the ticket. `reset` clears it.

`run` prints the agent's reply to the ticket and a short JSON summary.

Run the tests with:

```bash
PYTHONPATH=src python -m unittest discover -s tests
```
