# QA lifecycle routing

## Stage contract

| Stage | Minimum input | Success artifact | Route onward when |
| --- | --- | --- | --- |
| Discovery | Target repository and intended QA outcome | Context, execution surface, quality/risk profile, constraints, evidence gaps | At least one risk-based charter can be stated |
| Session planning | Discovery facts or explicit scope | Versioned session with charters, oracles, budgets, and stop conditions | Target identity and authorization are known |
| Execution | Planned charter and usable environment | Attempt-level observations and evidence references | Charter budget ends or an anomaly needs isolation |
| Reproduction | Candidate anomaly and baseline evidence | Confirmed, not-reproduced, dismissed, or still-candidate finding | Classification is honest and evidence is preserved |
| Reporting | Session artifacts | Decision-oriented report with scope, results, gaps, limitations, and disposition | Findings are normalized |
| Handoff | Confirmed finding plus product-planning inputs | Valid Bug payload | User explicitly requests ingestion or synchronization |

## Partial entry rules

- Start at discovery when the codebase, intended use, risks, or runnable surface are materially unknown.
- Start at discovery after an incident or a defect that reached users, and read `qa-discover`'s `references/escapes.md` before planning.
- Start at session execution when a reviewed charter or exact requested check already exists.
- Start at reproduction when there is a concrete observed anomaly with enough context to establish a baseline.
- Start at reporting when raw attempts/findings already exist and the user wants a defensible summary.
- Start at handoff only for a confirmed finding. A vague complaint or failed command is not enough.

## Completion

A workflow is complete when the requested scope is exhausted or a declared stop condition is met, every attempted action and limitation is recorded, findings are classified, and the user can tell what was and was not established. “No defects found” means only that no supported defect was found within the recorded scope and method.

Blocked is a valid terminal outcome when required authority, environment, test data, oracle, dependency, or target identity is unavailable. Record the missing evidence and the smallest next action that would unblock it.
