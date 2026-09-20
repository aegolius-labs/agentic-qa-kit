# Repository guidance

## Purpose

This repository packages host-portable agent skills and a deterministic, dependency-free Python evidence ledger for autonomous and assisted software quality assurance. Claude Code is the primary host and Codex is supported alongside it; `skills/` is the single source of truth for behavior on both.

## Invariants

- QA produces bounded evidence for explicit claims; passing checks never proves defect absence.
- Keep engineering evidence, policy evaluation, and residual-risk authority distinct.
- Discovery and planning are read-only by default. Destructive, production, privacy-sensitive, high-cost, or externally visible actions require explicit authorization at the point of action.
- Never weaken acceptance criteria, alter an oracle to make a run pass, or treat an LLM judgment as sole authority for an objective property.
- Preserve exact commands/actions, target revision, environment facts, all attempts, first failures, limitations, and evidence provenance.
- A suspected anomaly is not a confirmed defect until an independent oracle and controlled reproduction support it. Preserve `inconclusive` and `not-reproduced` outcomes honestly.
- The QA kit owns discovery, sessions, evidence, reproduction, and defect handoff. `agentic-backlog-kit` owns backlog hierarchy, prioritization, sprint planning, and GitHub reconciliation.
- Keep the runtime dependency-free unless a dependency provides a concrete, tested benefit that the standard library cannot provide safely.
- Do not put production data, credentials, secrets, or prohibited personal information into fixtures, logs, reports, or backlog payloads.

## Verification

Run:

```powershell
python -c "import sys, unittest; sys.path.insert(0, 'src'); suite=unittest.defaultTestLoader.discover('tests'); result=unittest.TextTestRunner(verbosity=2).run(suite); raise SystemExit(not result.wasSuccessful())"
python scripts/qa.py --help
```

Validate every changed skill with the bundled skill validator and validate the plugin manifest with the bundled plugin validator before handoff.
