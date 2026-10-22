---
name: qa-report
description: Assemble QA attempts and findings into a concise, auditable evidence package and decision-oriented session report. Use when the user wants QA results, evidence review, a session closeout, or a release-readiness input; do not present the report as residual-risk acceptance.
---

# Report QA evidence

1. Load the target session and only the linked evidence required for the report. Validate the manifest/session first; do not summarize invalid or internally inconsistent records as authoritative. Reporting consumes existing evidence: if the target session or linked records are unavailable, return a qualified `inconclusive` input and stop. Do not run replacement tests, initialize a ledger, install dependencies, or manufacture a substitute session unless the user separately asks to generate evidence.
2. Reconcile the target revision, dirty state, scope, charter objectives, executed attempts, oracles, findings, and evidence paths. Separate observed fact, interpretation, hypothesis, and limitation.
3. Check evidence quality: relevance to the claim, method/oracle validity, completeness, independence, reproducibility, provenance, freshness, privacy, and uncertainty. Missing evidence remains a gap, not an assumed pass.
4. Normalize findings by status and severity without converting severity into backlog priority. Preserve candidates, not-reproduced outcomes, dismissed anomalies, flaky signals, environment failures, and test/oracle defects.
5. State what the session established and what it did not. Report denominators and distributions when presenting rates; do not use one composite score as release authority.
6. Recommend a disposition of `acceptable`, `hold`, or `inconclusive` for the tested scope only. An accountable owner, not this report or agent, accepts consequential residual risk.
7. When closing the session, provide summary, limitations, residual risks, and next actions to `session-close`. Do not close while evidence is still being appended, or after an attempt or finding write that was rejected; a closed session cannot take it later.
8. Return a compact executive result followed by evidence details: scope/revision, methods, result counts, confirmed findings, candidates, gaps/limitations, disposition, evidence location, and next action.

Read [references/evidence-package.md](references/evidence-package.md) when reviewing completeness or preparing a consequential decision packet.
