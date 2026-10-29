# Escapes and incidents

Use when a defect reached users, or the user supplies an incident report or postmortem, so the next QA round learns from it.

## Authority

Read the ledger's confirmed findings (`summary`, then `show`) and only the incident material the user provided. Production logs, monitoring, support tickets and anything holding personal data each need their own approval. Without it, record the gap and plan from what was provided.

## For each escape

1. State the observed failure, its impact and its revision, from the material, not from memory.
2. Name the check that should have caught it and why it did not: no test, a weak oracle, a different environment, a flaky or retried suite, or a scope never chartered.
3. Check whether the cause is still present at the current revision, read-only, and say how you know.

## Planning

- Raise the area's risk: an escape is proof that detectability there was low.
- Add a regression charter whose oracle is the observed failure. Cite the incident or finding in its risks.
- Prefer the test layer that should have caught it, and say which one.
- Never copy personal data, customer names or credentials from the incident into the ledger.
- An escape is evidence about the checks, not new intent: do not change the expected behavior because of it. If the material contradicts the documented behavior, record that as an open question.
