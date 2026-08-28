# Reproduction contract

## Evidence threshold

Confirmation requires all of:

- Exact target revision and dirty-state disclosure, or an explicit identity limitation.
- Preconditions, inputs, and ordered steps.
- Expected and actual behavior with an independent oracle.
- Attempt count and outcome sequence; first failure preserved.
- Environment/configuration facts material to the behavior.
- At least one durable evidence reference.
- Reproducibility classification and confidence.
- Known limitations and untested competing hypotheses.

Repeated execution is not always necessary when one valid execution proves a deterministic invariant breach or irreversible state difference, but explain why the single witness is sufficient. Repeats of a stochastic or concurrency-sensitive result do not become independent evidence merely because there are more runs.

## Minimization rules

Preserve the failure predicate while reducing one dimension at a time:

1. Input/data.
2. State/setup.
3. Action sequence.
4. Configuration and dependency set.
5. Concurrency/timing perturbation.
6. Environment/service topology.

Re-run the minimized witness and a negative control. If minimization changes the observed mechanism or invalidates the oracle, restore the last valid witness.

## Root cause

Do not infer root cause from the failing line, exception text, or correlated change alone. Record `unknown` or a clearly labeled hypothesis until change isolation, instrumentation, differential behavior, or a verified fix supplies stronger causal evidence.
