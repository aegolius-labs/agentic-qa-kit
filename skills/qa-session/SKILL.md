---
name: qa-session
description: Plan and execute a bounded QA session against a codebase, recording exact attempts, observations, oracles, evidence, and candidate findings. Use for exploratory, functional, regression, static, integration, or scoped non-functional testing, including checking whether one behavior holds by running the narrowest existing tests under a time or attempt limit; do not use to claim release approval or to fix defects unless separately requested.
---

# Run a bounded QA session

1. Load repository instructions, `.agentic-qa/manifest.json` when present, and only the selected session/charter. Confirm revision and dirty state first.
2. If no reviewed charter exists, write the minimum one: risk, quality attribute, objective, scope, method, independent oracle, minutes/attempt budget, evidence, stop conditions.
3. Verify authorization and prerequisites right before each effectful action. Authorized existing local checks may run; dependency installation, source/test edits, external services, live-account browsers, sensitive data, load/fault injection and production each need their own scope and approval. A bounded concurrency probe of the target's own local commands inside a disposable temporary directory, touching nothing outside it, is a local check.
4. Prefer the narrowest canonical command. Record environment and entropy facts: tool/runtime version, configuration, fixture/data identity, locale/time, seed/order, services, network.
5. Record every executed attempt with `attempt-add`, including first failures and diagnostic retries. Do not replace an observation with a later pass or infer a business verdict from an exit code. A rejected ledger write changes nothing: check each exit status before the next write; never chain writes with `;`.
6. Compare observations with the declared oracle. Create a candidate finding only when expected and actual behavior differ within scope; distinguish product behavior, test/oracle failure, environment failure, flakiness and missing evidence.
7. Route suspected product defects to `$qa-reproduce`. Stop on the charter budget, an authorization boundary, evidence contamination, target drift, a critical invariant breach, or an environment invalidating the method.
8. Return scope/revision, charter status, attempts, outcomes, evidence paths, candidate findings, gaps, budget used and next action. Repair only if asked.

Read [session-design](references/session-design.md) for charters, retries or risky techniques, and the one pack the charter needs: [functional-design](references/functional-design.md) for specified rules, ranges, states or flows; [performance](references/performance.md) for speed, [resilience](references/resilience.md) for faults, [accessibility-i18n](references/accessibility-i18n.md) for access or locales, [data-integrity](references/data-integrity.md) for keys, invariants or paging, [suite-trust](references/suite-trust.md) for flaky tests, [observability](references/observability.md) for logs or diagnosis.
