# QA artifact contracts

## Project manifest

`.agentic-qa/manifest.json` contains stable target-level policy:

- schema version and project name;
- default risk tier, budgets, and evidence root;
- selected quality attributes and measurable claim notes;
- allowed, approval-required, and forbidden action classes; and
- backlog mode and target plugin identity.

It contains no credentials, live environment identifiers, or production data.

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
- once a finding leaves `candidate`, its `title`, `summary`, `expected`, `actual` and `oracle` are fixed. A later observation is a new attempt, or a continuation when the session is closed.

## Concurrent writers

Every change to a session holds an exclusive operating-system lock on `.session.lock` beside `session.json` for the whole read-modify-write, so parallel writers are serialized and none loses another's record. The lock is released when its holder exits, including after a crash. It covers processes on one machine sharing a local filesystem; network filesystems may not honor it.

## Backlog handoff

The export is a single Agentic Backlog Kit `Bug` add payload. It requires explicit planning inputs and includes the QA session/finding IDs in the description. Export does not ingest or synchronize the item.
