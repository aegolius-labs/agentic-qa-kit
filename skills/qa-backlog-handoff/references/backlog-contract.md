# Backlog handoff contract

## Required planning fields

```json
{
  "parent": null,
  "depends_on": [],
  "impact": 1,
  "effort": 1,
  "business_value": 1,
  "enabler_value": 0,
  "status": "Backlog",
  "maturity": "refined",
  "sprint": null
}
```

Impact, Effort, and Business Value are integers from 1 to 5. Enabler Value is 0 to 5. The example values illustrate shape only; never substitute them for owner judgment.

## Authority split

Agentic QA Kit owns:

- QA session and finding identities;
- severity, confidence, expected/actual behavior;
- reproduction steps and reproducibility;
- evidence, limitations, and QA acceptance criteria; and
- generation of one proposed Bug payload.

Agentic Backlog Kit owns:

- stable backlog item identity;
- hierarchy and dependency validation;
- Impact, Effort, Business Value, Enabler Value, and priority;
- workflow status and sprint planning; and
- GitHub Issues/Projects plan, confirmation, apply, and verification.

The handoff does not make QA evidence the backlog system of record and does not make backlog priority part of the QA verdict.
