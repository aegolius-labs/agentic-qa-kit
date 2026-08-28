---
name: qa-backlog-handoff
description: Convert a confirmed QA finding into a validated Agentic Backlog Kit Bug payload and, when explicitly requested, feed it into that kit. Use after reproduction and evidence review; do not use for candidate findings, prioritization, sprint planning, or implicit GitHub synchronization.
---

# Hand off a confirmed defect

1. Validate the QA session and load only the confirmed finding. Reject candidate, not-reproduced, dismissed, evidence-free, or incomplete findings.
2. Review the title, summary, expected/actual behavior, independent oracle, minimized reproduction, evidence, limitations, and acceptance criteria. Remove secrets or prohibited personal information; retain stable QA session/finding IDs and target revision.
3. Collect the Agentic Backlog Kit planning fields: parent, dependencies, Impact, Effort, Business Value, Enabler Value, workflow status, maturity, and sprint. Do not infer business priority or effort from QA severity. Use `maturity: refined` when planning inputs or acceptance criteria still need owner review.
4. Write those explicit fields to a temporary JSON file under `.agentic-qa/` and run `backlog-export`. The output must be one `Bug` add payload compatible with Agentic Backlog Kit.
5. By default, stop after showing the validated payload and its evidence links.
6. If the user explicitly asks to feed the backlog and `agentic-backlog-kit` is available, use its `$backlog-ingest` workflow or `item-add` command, then validate and show the resulting stable backlog ID. Do not sync to GitHub unless the user separately requests that backlog workflow.
7. Return the QA session/finding IDs, payload or created backlog ID, maturity, parent/dependencies, planning values supplied, evidence linkage, and whether remote synchronization remains pending.

Read [references/backlog-contract.md](references/backlog-contract.md) for field boundaries and the exact two-kit authority split.
