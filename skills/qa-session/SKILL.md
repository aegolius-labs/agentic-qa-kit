---
name: qa-session
description: Plan and execute a bounded QA session against a codebase, recording exact attempts, observations, oracles, evidence, and candidate findings. Use for exploratory, functional, regression, static, integration, or scoped non-functional testing; do not use to claim release approval or to fix defects unless separately requested.
---

# Run a bounded QA session

1. Load applicable repository instructions, the target `.agentic-qa/manifest.json` when present, and only the selected session/charter details. Confirm target revision and dirty state before execution.
2. If no reviewed charter exists, create the minimum charter needed for the request: risk, quality attribute, objective, scope, method, independent oracle, minutes/attempt budget, evidence to retain, and stop conditions.
3. Verify authorization and environment prerequisites immediately before each effectful action. Existing local checks may be run when authorized; dependency installation, source/test edits, external services, browsers with live accounts, sensitive data, load/fault injection, and production require their own scope and approval.
4. Prefer the repository's canonical, narrowest useful commands first. Keep environment and entropy facts visible: tool/runtime version, target revision, configuration, fixtures/data identity, locale/time, seed/order, services, and network assumptions when material.
5. Record every executed attempt with `attempt-add`, including first failures and diagnostic retries. Do not replace an observation with a later pass or infer a business verdict from an exit code.
6. Compare observations against the declared oracle. Create a candidate finding only when expected and actual behavior differ under the stated scope; distinguish product behavior, test/oracle failure, environment failure, flakiness, and missing evidence.
7. Route suspected product defects to `$qa-reproduce`. Stop on the charter budget, an authorization boundary, evidence contamination, target drift, a critical invariant breach, or an environment state that invalidates the method.
8. Return scope/revision, charter status, attempts and outcomes, evidence paths, candidate findings, gaps, consumed budget, and recommended next action. Do not implement repairs unless asked.

Read [references/session-design.md](references/session-design.md) when creating a charter, selecting retries, or running a non-functional or risky technique.
