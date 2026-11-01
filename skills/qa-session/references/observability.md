# Observability session pack

Use when a charter's quality attribute is `observability`: whether logs, metrics, traces and errors let someone diagnose a failure.

## Authority: fail closed

Local checks: triggering documented failure paths of a target the session started, and reading the signals it writes locally.

Each of these needs its own approval:
- querying production or shared log stores, dashboards, tracing or alerting;
- editing code or configuration to add signals;
- sending test signals to a shared collector.

Without approval, record the attempt as `inconclusive` and stop.

## Signal contract

Name the documented contract, or record that none exists. Per failure: the signal, its fields (correlation ID, entity, cause), level, metric and label, and what must never appear (secrets, personal data).

## Environment

Record:
- revision, configuration and log level;
- signal sinks and formats;
- the trigger for each failure path;
- clock and time zone.

## Oracle

Trigger one known failure at a time, then answer from the signals alone, without reading the code: which request and entity failed, at which step, and why. The failure is diagnosable when that answer names the triggered cause.

Then check the contract:
- every documented field is present on every failure path;
- metric labels separate the causes;
- no secret or personal data appears.

A generic message such as "failed", a swallowed exception or a missing correlation ID is a finding. Copy a leaked value into the ledger only masked.

## Uncertainty

- Paths not triggered are not evaluated. List them.
- Local sinks and levels can differ from production.
- Sampling, buffering or rotation can drop signals.

## Stop conditions

Stop on any of these:
- an authorization boundary;
- continuing would need a code or configuration change;
- signals leaking beyond the target;
- target drift;
- the charter budget.

## Evidence

Keep:
- the trigger command for each path;
- the signal excerpts, with leaked values masked;
- the diagnosis made from signals alone and the actual cause;
- a contract table: path, field, present or missing.
