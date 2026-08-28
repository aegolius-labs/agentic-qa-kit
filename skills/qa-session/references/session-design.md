# Session design

## Charter minimum

- Identity and objective.
- Risk scenario and quality attribute.
- Included and excluded target scope.
- Method and why it reduces the named uncertainty.
- Oracle: expected relation, state, threshold, or independently calculated result.
- Environment, fixtures/data, and controlled variables.
- Time and attempt budget.
- Evidence to retain.
- Stop conditions and authorization boundaries.

## Execution ladder

Use increasing scope/fidelity only when the previous layer leaves material uncertainty:

1. Read-only review, configuration/schema/static checks.
2. Focused unit/component/contract checks.
3. Integration with versioned fakes or disposable local services.
4. Broader system/UI checks in an isolated environment.
5. Performance, recovery, fault, external, or production-shaped work under an explicit experiment and authorization.

## Retry semantics

- A retry diagnoses; it does not erase the first outcome.
- Preserve fixed target, inputs, environment, order, and seed when checking reproducibility.
- Then vary one plausible mechanism at a time: order, clock, seed, resource pressure, service latency, or concurrency.
- `pass after retry` is suspected nondeterminism until explained.
- Stop repeated retries when the charter budget is exhausted or new runs no longer add information.

## Verdict discipline

- `pass`: the recorded observation satisfied the declared oracle in the stated context.
- `fail`: the observation contradicted the oracle and the execution remained valid.
- `inconclusive`: the oracle, environment, data, or observation was insufficient.
- `error`: the method did not complete validly.

Never average a critical invariant violation into an otherwise successful session.
