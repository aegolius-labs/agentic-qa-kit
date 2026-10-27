---
name: qa-backlog-handoff
description: Turn a QA finding into Agentic Backlog Kit work: check eligibility, export a validated Bug payload for a confirmed finding, and, when explicitly requested, feed it into that kit. Use for any request to make a backlog item, bug, or issue from a QA finding, including a candidate or inconclusive one, which it rejects with the reason; do not use for prioritization, sprint planning, or implicit GitHub synchronization.
---

# Hand off a confirmed defect

1. Validate the QA session and load only the confirmed finding from the explicit target root. Reject candidate, not-reproduced, dismissed, evidence-free, or incomplete findings. When an evaluator supplies a disposable fixture root, stay within it; do not search unrelated sibling or user backlogs.
2. Review the title, summary, expected/actual behavior, independent oracle, minimized reproduction, evidence, limitations, and acceptance criteria. Remove secrets or prohibited personal information; retain stable QA session/finding IDs and target revision.
3. Collect the Agentic Backlog Kit planning fields: parent, dependencies, Impact, Effort, Business Value, Enabler Value, workflow status (one of the backlog manifest's `workflow.statuses`), maturity, and sprint. Do not infer business priority or effort from QA severity. Use `maturity: refined` when planning inputs or acceptance criteria still need owner review.
4. Write those explicit fields to a temporary JSON file under `.agentic-qa/` and run `backlog-export`. The output must be one `Bug` add payload compatible with Agentic Backlog Kit.
5. By default, stop after showing the validated payload and its evidence links.
6. If the user asks to prepare synchronization, use the Agentic Backlog Kit synchronization workflow. Prefer an explicitly supplied recorded remote snapshot for deterministic offline planning; do not fabricate remote state or query example coordinates. Stop after the plan and digest. Do not ingest unless requested, and never apply without the backlog workflow's exact digest confirmation.
7. If the user explicitly asks to feed the backlog and `agentic-backlog-kit` is available, use its `$backlog-ingest` workflow or `item-add` command against the explicit backlog root, then validate and show the resulting stable backlog ID. Do not fall back to another backlog. Do not sync to GitHub unless the user separately requests that backlog workflow.
8. Return the QA session/finding IDs, payload or created backlog ID, maturity, parent/dependencies, planning values supplied, evidence linkage, and whether remote synchronization remains pending.

Read [references/backlog-contract.md](references/backlog-contract.md) for field boundaries and the exact two-kit authority split.
