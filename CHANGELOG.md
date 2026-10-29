# Changelog

All notable changes to this project will be documented here.

The format follows Keep a Changelog, and releases use semantic versioning.
Write new entries in the Unreleased section; the release workflow stamps the
computed version and promotes that section when it publishes.

## [Unreleased]

### Added

- Escape-driven discovery (Q12, M5): `qa-discover` gains an escapes reference.
  When a defect reached users or an incident is supplied, discovery reads only
  the provided material and names the check that missed it. It then raises
  that area's risk and adds a regression charter that cites the incident. It
  never copies personal data into the ledger, and an escape is not treated as
  new intent. `qa-workflow` starts incident follow-ups at discovery, and the
  `qa-discover` description names them.
- Q12-G01 lane: `scripts/q12_claude_code.py` plans a QA round from a
  postmortem that names a customer. The 2026-10-29 result is in
  `evals/results/q12-claude-code-2026-10-29.json`.
- `qa-discover`'s routing questions name the suite-trust pack.

## [0.8.0] - 2026-10-29

### Added

- Suite-trust session pack (Q11, M5): a `qa-session` reference for flaky,
  order-dependent and retried tests. It names the trust claim (determinism,
  isolation, hermeticity or signal) and varies one entropy source at a time:
  hash seed, order, locale or time zone, and parallelism. It then classifies
  each cause as a product defect, a test defect or the environment. Editing
  tests or CI, installing rerun or random-order plugins, and rerunning shared
  CI each need approval, and no test is skipped, retried away or quarantined to
  make a suite pass.
- Q11-G01 lane: `scripts/q11_claude_code.py` runs two fresh sessions on a
  fixture whose CI retries a suite that fails on about half of hash seeds and
  hides an order-dependent test. The 2026-10-29 result is in
  `evals/results/q11-claude-code-2026-10-29.json`.

### Changed

- The other non-functional packs are trimmed so the activation budget holds
  with a fifth pack.

## [0.7.0] - 2026-10-29

### Added

- Q07 decision record (`docs/q07-mcp-decision.md`): keep the skills-only
  architecture. `scripts/q07_measure.py` measured 18 retained lane
  transcripts. 23% of tool calls went on learning payload shapes, and 23 of
  100 ledger writes were rejected, mostly for CLI ergonomics an MCP server
  would not fix.

### Changed

- `finding-add` and `finding-update` count `reproduction.attempts` from
  `attempt_ids` when the caller leaves it out. A supplied count is still
  checked, and the error states the expected number.
- `summary` takes the session ID positionally, as `show` and `session-close`
  do. `--session` still works.

## [0.6.1] - 2026-10-29

### Added

- Q05-G01 lane: `scripts/q05_claude_code.py` sends one non-functional request
  per pack through the installed plugin, two of them needing an action the
  packs reserve for approval, and records which pack each session read and how
  the ledger marks its attempts. The 2026-10-29 result is in
  `evals/results/q05-claude-code-2026-10-29.json`.

### Fixed

- `qa-session` names what each non-functional pack covers instead of only its
  quality attribute, so a request about paging or consistency reaches the
  data-integrity pack (Q05-G01-F01). The data-integrity pack lists paging.

## [0.6.0] - 2026-10-29

### Added

- Non-functional session packs (Q05): `qa-session` references for performance,
  resilience and recovery, accessibility with compatibility and i18n, and data
  integrity. Each states its workload, fault model or population, environment,
  oracle, uncertainty, stop conditions and evidence. Each opens with an
  authority section that fails closed: load, fault injection, live accounts,
  shared stores and real data need their own approval, and without it the
  attempt is `inconclusive` and the session stops. Security stays with a
  dedicated workflow.

### Changed

- The `qa-session` body is tightened to route to one technique pack per
  charter within the activation budget.

## [0.5.0] - 2026-10-29

### Added

- `backlog-export` sets the payload's `source` to
  `agentic-qa-kit:session=<session>;finding=<finding>`. Agentic Backlog Kit
  0.20.0 and later keep it unique and refuse a second item for the same
  finding, so a repeated handoff no longer creates a duplicate Bug (Q06-F02).
  An older backlog kit refuses the field as unknown; update it before handing
  off. The Seam B fixture is refreshed from a current export on both sides.

### Fixed

- `scripts/q06_interop.py` resolves a relative `AGENTIC_BACKLOG_KIT` path, so
  its test no longer runs the backlog kit from the wrong directory.

## [0.4.2] - 2026-10-29

### Added

- `scripts/q04_claude_code.py`, which runs the Q02 fixtures that carry written
  rules through the installed plugin and reads the obligation ledger each
  session left (Q04-G01), with its first recorded result.

### Fixed

- `examples/session.json` and `examples/attempt.json` now show charter
  `obligations` and attempt `obligation_ids`. Agents copy these examples for
  payload shapes, and without them two of three Q04-G01 sessions read the
  design pack but recorded no obligation ledger (Q04-G01-F01).

## [0.4.1] - 2026-10-27

### Added

- `scripts/q06_interop.py`, an offline check of the backlog handoff against a
  real Agentic Backlog Kit checkout (Q06), with its first recorded result.

### Fixed

- The backlog handoff example used status `Backlog`, which the backlog kit's
  default workflow does not define. It now uses `Inbox`, and the contract says
  the status must come from the backlog manifest's `workflow.statuses`
  (Q06-F01).

## [0.4.0] - 2026-10-27

### Added

- Functional test-design pack (Q04): a `qa-session` reference that picks
  partition, boundary, decision-table, state-transition, scenario,
  combinatorial or property techniques from the specification's shape, and
  requires an obligation ledger with independent oracles before execution.
- Charters accept optional `obligations` (id, technique, source, statement,
  oracle), and attempts accept `obligation_ids` naming obligations of their own
  charter. `summary` reports obligation coverage as total, exercised,
  inconclusive and unexercised: coverage of the design model, not defect
  absence.

### Changed

- The skill activation budget counts a skill body plus its largest reference,
  since a skill reads only the reference its trigger selects. Each reference
  stays capped at 3 KB.

## [0.3.0] - 2026-10-22

### Added

- Evidence-file digests (Q03-G01). Attempt and finding writes record a
  SHA-256 digest of each evidence file inside the repository, and refuse a
  supplied digest that does not match the file. `validate` fails when a
  digested file changed and reports `evidence_verified` and `evidence_missing`.

## [0.2.1] - 2026-10-22

### Fixed

- The ledger now stores sessions under the manifest's `defaults.evidence_root`
  instead of always using `.agentic-qa/sessions` (Q09-F05). A root that
  resolves outside the repository, for example through a symlink, is refused.
  Sessions already written under an earlier root are not moved.

## [0.2.0] - 2026-10-22

### Added

- Chained evidence receipts (Q03). New sessions use schema version 2 and seal
  every accepted write in a SHA-256 receipt that links to the one before it.
  `validate` fails on a session changed outside the ledger, an altered,
  removed or reordered receipt, or a dropped last write. A broken session
  takes no further writes. `summary` and `show` report `integrity`.
- `aqk migrate <session>` seals a schema-version-1 session as version 2.
  Version-1 sessions stay valid and are reported as `unchained`.

### Changed

- `show` leaves a session's receipt chain out and reports its integrity
  status and receipt count instead.
- `qa-report` treats a broken integrity check as evidence contamination.

## [0.1.3] - 2026-10-22

### Fixed

- `qa-session` tells the agent to check each ledger write's exit status before
  the next one and never to chain ledger writes with `;`. `qa-report` does not
  close a session after a rejected attempt or finding write. A Q02 run had
  closed a session without the findings whose write had been rejected
  (Q02-F01).

## [0.1.2] - 2026-10-22

### Fixed

- Once a finding leaves `candidate`, the ledger rejects changes to its
  severity, acceptance criteria and reproduction preconditions, steps and
  reproducibility (Q09-F04, owner decision 2026-10-22). Linking a new attempt
  still updates `reproduction.attempts`.

## [0.1.1] - 2026-10-19

### Changed

- `qa-session` and `qa-reproduce` state that a bounded concurrency probe
  confined to a disposable temporary directory is a local check and needs no
  approval (Q01-F08, owner decision 2026-10-19). Load, fault injection and
  anything outside that directory still need approval.

## [0.1.0] - 2026-10-19

First public release of Agentic QA Kit.

### Added

- Six host-portable skills: `qa-workflow`, `qa-discover`, `qa-session`,
  `qa-reproduce`, `qa-report` and `qa-backlog-handoff`, from one `skills/`
  tree for both Claude Code and Codex.
- A dependency-free evidence ledger (`scripts/qa.py`, installed as `aqk`).
  It stores sessions, charters, attempts, findings, continuations and decisions
  as validated JSON under `.agentic-qa/`, and exports a confirmed finding as
  one Agentic Backlog Kit `Bug` payload.
- Claude Code support as the primary host, with Codex alongside it. Manifest
  parity and the plugin validator run in CI on Linux, Windows and macOS with
  Python 3.11 to 3.14.
- The Q01 activation suite: 36 cases covering six categories for each skill, and
  a headless Claude Code lane runner (`scripts/q01_claude_code.py`). The
  2026-10-16 lane result is committed under `evals/results/`.
- `qa-session` and `qa-backlog-handoff` activate for the requests the first
  lane run missed (Q01-F07); the rerun passed 6 of 6.
- The first self-QA run (Q09): two sessions through the installed plugin,
  reported in `docs/q09-self-qa-2026-10-16.md`.
- Byte budgets for skill text and ledger output (`scripts/budgets.py`),
  enforced in CI and release preflight.
- Organization-managed releases: a release-bearing Conventional Commit on
  `main` computes the version, stamps it, builds and checks the distributions,
  and publishes an immutable GitHub Release.
- License (PolyForm Noncommercial 1.0.0, with commercial terms in
  `COMMERCIAL.md`), security, support and contribution policies.

### Fixed

- Concurrent writers to one session no longer lose records: every session
  write holds an exclusive file lock (Q09-F01).
- `finding-update` no longer rewrites a finding's recorded observation or
  erases its evidence; history fields are append-only (Q09-F02).

### Known limitations

See [Limitations](README.md#limitations). In short:

- Session writes are serialized with an operating-system file lock, which
  network filesystems may not honor.
- Q01 evidence covers the skills as written at a commit, on the headless Claude
  Code CLI, one run per case. It is not evidence about this published artifact,
  the desktop surface, or how often a case passes.
- The authorization rule for bounded local concurrency probes is not yet
  stated in the skills (Q01-F08).

