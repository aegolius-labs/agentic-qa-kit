---
name: qa-session
description: Plan and execute a bounded QA session against a codebase, recording exact attempts, observations, oracles, evidence, and candidate findings. Use for exploratory, functional, regression, static, integration, or scoped non-functional testing, including checking whether one behavior holds by running the narrowest existing tests under a time or attempt limit; do not use to claim release approval or to fix defects unless separately requested.
---

# Run a bounded QA session

1. Load repository instructions, the target `.agentic-qa/manifest.json` when present, and only the selected session/charter. Confirm target revision and dirty state first.
2. If no reviewed charter exists, write the minimum one: risk, quality attribute, objective, scope, method, independent oracle, minutes/attempt budget, evidence, stop conditions.
3. Verify authorization and prerequisites immediately before each effectful action. Authorized existing local checks may run; dependency installation, source/test edits, external services, live-account browsers, sensitive data, load/fault injection and production each need their own scope and approval. A bounded concurrency probe of the target's own local commands inside a disposable temporary directory, touching nothing outside it, is a local check.
4. Prefer the narrowest canonical commands. Record material environment and entropy facts: tool/runtime version, revision, configuration, fixture/data identity, locale/time, seed/order, services, network.
5. Record every executed attempt with `attempt-add`, including first failures and diagnostic retries. Do not replace an observation with a later pass or infer a business verdict from an exit code. A rejected ledger write changes nothing, so check each write's exit status before the next one; never chain ledger writes with `;`.
6. Compare observations against the declared oracle. Create a candidate finding only when expected and actual behavior differ under the stated scope; distinguish product behavior, test/oracle failure, environment failure, flakiness, and missing evidence.
7. Route suspected product defects to `$qa-reproduce`. Stop on the charter budget, an authorization boundary, evidence contamination, target drift, a critical invariant breach, or an environment state that invalidates the method.
8. Return scope/revision, charter status, attempts and outcomes, evidence paths, candidate findings, gaps, consumed budget and next action. Do not repair unless asked.

Read [session-design](references/session-design.md) for charters, retries or risky techniques, and the one technique pack the charter calls for: [functional-design](references/functional-design.md) for specified rules, ranges, states or flows; [performance](references/performance.md), [resilience](references/resilience.md), [accessibility-i18n](references/accessibility-i18n.md) or [data-integrity](references/data-integrity.md) for those quality attributes.
