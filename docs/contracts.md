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

- stable ID, objective, mode, lifecycle status, and timestamps;
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

## Backlog handoff

The export is a single Agentic Backlog Kit `Bug` add payload. It requires explicit planning inputs and includes the QA session/finding IDs in the description. Export does not ingest or synchronize the item.
