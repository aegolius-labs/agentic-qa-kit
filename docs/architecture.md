# Architecture

## Control loop

Agentic QA Kit implements the following information flow:

```text
context and intended use
  -> quality claims and risk hypotheses
  -> repository and runtime discovery
  -> bounded QA charters
  -> attempt-level observations
  -> candidate findings
  -> controlled reproduction and minimization
  -> evidence package and limitations
  -> confirmed defect handoff
  -> future regression and risk-model learning
```

Three authorities remain distinct:

1. Engineering mechanisms and agents produce evidence.
2. Versioned policy evaluates evidence and may make a pre-authorized bounded decision.
3. An accountable owner accepts consequential residual risk.

A tool, test runner, scanner, model judge, or dashboard is not its own risk owner.

## Components

1. Six focused skills route full and partial workflows.
2. `scripts/qa.py` exposes compact, deterministic commands over a dependency-free Python package.
3. A target repository's `.agentic-qa/manifest.json` declares quality defaults, evidence location, authorization boundaries, and backlog mode.
4. Each `.agentic-qa/sessions/<id>/session.json` binds target identity, scope, charters, attempts, findings, gaps, and disposition.
5. Append commands validate identities and lifecycle invariants before atomic replacement of the session record.
6. Backlog export accepts only confirmed findings with evidence and explicit planning inputs.

## Session state model

```text
planned -> running -> completed
                  \-> blocked
```

`completed` and `blocked` are terminal in schema version 1. Reopening requires a new session linked through its objective or evidence rather than rewriting history.

Finding states are `candidate`, `confirmed`, `not-reproduced`, and `dismissed`. Only `candidate -> confirmed|not-reproduced|dismissed` is allowed. A confirmed finding may be handed off; other states remain evidence but not backlog defects.

## Safety boundary

- Discovery is read-only.
- The ledger writes only under the selected target's `.agentic-qa/` directory or an explicit export path.
- The ledger does not execute test commands, browse applications, call external services, mutate production, or synchronize a backlog.
- Skills use tools already present in Codex and remain subject to the host's sandbox and approval rules.
- A full workflow does not broaden user authority. When a useful technique requires destructive, external, production, sensitive-data, or material-cost effects, the session pauses at that action boundary.

## Backlog interoperability

Agentic QA Kit outputs one Agentic Backlog Kit `Bug` payload. Planning values such as Impact, Effort, Business Value, Enabler Value, parent, and workflow status come from explicit inputs; QA severity is not silently converted into product priority. The sibling kit validates, ingests, prioritizes, plans, and synchronizes the payload.
