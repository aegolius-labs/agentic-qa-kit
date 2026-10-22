---
name: qa-reproduce
description: Reproduce, isolate, and minimize a suspected software defect while preserving controls, attempts, evidence, and uncertainty. Use when an anomaly, failed check, flaky behavior, or defect report needs confirmation; do not use to invent root cause or silently repair the product.
---

# Reproduce a suspected defect

1. Load the candidate finding and linked attempts when available. Preserve the original target revision, command/action, inputs, expected/actual behavior, environment, first failure, and evidence before changing any variable.
2. Validate the oracle independently. Check whether the expectation comes from a requirement, invariant, public contract, reviewed calculation, state relation, or trustworthy reference behavior, not merely from the implementation under test or an LLM opinion.
3. Establish a controlled baseline in the same valid environment. Re-run within the configured attempt budget and record every outcome; do not label a one-off infrastructure error as a product defect.
4. Form explicit competing hypotheses: product fault, test/oracle fault, fixture/data issue, environment/configuration issue, order/timing/concurrency nondeterminism, dependency drift, or operator error.
5. Change one material variable at a time. Minimize input, setup, action sequence, dependent services, and elapsed time while preserving the observed failure and valid oracle. Do not modify product code or tests unless the user asked for a diagnostic patch.
6. Probe nearby boundaries, negative controls, and a known-good comparison when they improve causal discrimination. Keep destructive, external, sensitive, load, fault-injection, and production actions behind explicit authorization. A bounded concurrency probe confined to a disposable temporary directory is a local check, not load or fault injection.
7. Classify honestly:
   - `confirmed`: controlled evidence repeatedly or otherwise sufficiently supports a product-contract violation.
   - `not-reproduced`: valid attempts did not reproduce it; retain the original observation and limits.
   - `dismissed`: evidence supports a non-product explanation or invalid oracle.
   - `candidate`: evidence remains insufficient or conflicting.
8. Update the finding rather than replacing history. Record reproduction steps, reproducibility, attempt IDs, evidence, limitations, confidence, acceptance criteria, and root cause as `unknown` unless independently established. The confirming update fixes severity, reproduction, and acceptance criteria; later attempts only append. If the source session is terminal, do not reopen or rewrite it: create a new session with `continuation_of.session_id` and `continuation_of.finding_id`, append the new attempt there, and report the linked outcome without creating a replacement finding.

Read [references/reproduction-contract.md](references/reproduction-contract.md) before confirming, dismissing, or minimizing a finding.
