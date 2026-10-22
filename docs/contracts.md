# QA artifact contracts

## Project manifest

`.agentic-qa/manifest.json` contains stable target-level policy:

- schema version and project name;
- default risk tier, budgets, and evidence root;
- selected quality attributes and measurable claim notes;
- allowed, approval-required, and forbidden action classes; and
- backlog mode and target plugin identity.

It contains no credentials, live environment identifiers, or production data.

`defaults.evidence_root` is where the ledger keeps sessions, relative to the
repository root; the default is `.agentic-qa/sessions`. It must resolve inside
the repository. Changing it does not move sessions already written: the ledger
reads only the current root.

A bounded concurrency probe that runs the target's own local commands inside a
disposable temporary directory, touching nothing outside it, belongs to
`run_existing_local_checks`, not `run_load_or_fault_injection` (owner decision,
2026-10-19). A probe that reaches shared state, external services or resource
exhaustion is still load or fault injection.

## Session

A session binds:

- stable ID, objective, mode, lifecycle status, timestamps, and optional validated continuation lineage to a terminal source session/finding;
- target root, immutable revision when available, and dirty-state disclosure;
- inclusion/exclusion scope and context;
- charters with risks, methods, oracles, budgets, and stop conditions;
- attempt-level records;
- findings and evidence gaps; and
- a final disposition with limitations when closed.

The target revision may be `unknown` when the directory is not under version control, but the limitation must stay visible. Do not pretend an unstable working tree is an immutable test item.

## Attempt

An attempt records the action actually performed, not a proposed command:

- stable attempt and charter IDs;
- timestamp and duration when known;
- command or manual action;
- environment facts and controlled variables;
- outcome: `pass`, `fail`, `inconclusive`, or `error`;
- exit code when applicable;
- observation and oracle used; and
- evidence references with kind, location, and optional digest.

Retries never replace the first result.

## Finding

A finding records title, quality attribute, severity, confidence, status, summary, expected and actual behavior, controlled reproduction, evidence, limitations, and acceptance criteria. Severity describes consequence; it is not backlog priority. Root cause remains `unknown` until independently supported.

Confirmed findings require:

- at least one reproduction step;
- a declared reproducibility result;
- at least one evidence reference;
- non-empty expected and actual behavior; and
- an independent oracle description.

A finding update keeps its history:

- `recorded_at` never changes;
- `attempt_ids`, `evidence` and `limitations` only grow, and existing entries are never removed or rewritten; and
- once a finding leaves `candidate`, its `title`, `summary`, `expected`, `actual`, `oracle`, `severity`, `acceptance_criteria` and reproduction `preconditions`, `steps` and `reproducibility` are fixed (owner decision on Q09-F04, 2026-10-22). `reproduction.attempts` still counts the linked attempts as they grow. A later observation is a new attempt, or a continuation when the session is closed.

## Receipts

A schema-version-2 session carries `receipts`, one per accepted write:
`session-create`, `attempt-add`, `finding-add`, `finding-update`,
`session-close` and `migrate`. Each receipt records its sequence number,
operation, subject ID, time, the digest of the receipt before it, and the
SHA-256 digest of the whole session except its receipts, as it stood after the
write. The receipt's own digest covers all of those fields. Digests are taken
over canonical JSON: sorted keys, no insignificant whitespace, UTF-8.

`validate` recomputes every chain and fails when a session disagrees with it.
That covers an edit made outside the ledger, an altered, removed or reordered
receipt, and a dropped last receipt. A session that fails takes no further
writes, because a new receipt would seal over the change. `summary` and `show`
report `integrity` as `chained`, `broken` or `unchained`, and `show` leaves
the chain itself out.

What a chain does not prove:

- that any recorded observation is true;
- that nobody rewrote the session together with every receipt after the
  change, because the chain carries no secret;
- that a session was not rolled back to an earlier sealed state, receipts
  included.

It makes an unforged change visible. It does not authenticate the writer.

Sessions created before schema version 2 stay valid and `unchained`. Writes to
them still work and add no receipts. `migrate <session>` seals one as version
2 with a single `migrate` receipt. Everything before that receipt is
unverified, and the operation name records that.

## Concurrent writers

Every change to a session holds an exclusive operating-system lock on `.session.lock` beside `session.json` for the whole read-modify-write, so parallel writers are serialized and none loses another's record. The lock is released when its holder exits, including after a crash. It covers processes on one machine sharing a local filesystem; network filesystems may not honor it.

## Backlog handoff

The export is a single Agentic Backlog Kit `Bug` add payload. It requires explicit planning inputs and includes the QA session/finding IDs in the description. Export does not ingest or synchronize the item.
