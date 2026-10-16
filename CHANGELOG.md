# Changelog

All notable changes to this project will be documented here.

The format follows Keep a Changelog, and releases use semantic versioning.
Write new entries in the Unreleased section; the release workflow stamps the
computed version and promotes that section when it publishes.

## [Unreleased]

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
