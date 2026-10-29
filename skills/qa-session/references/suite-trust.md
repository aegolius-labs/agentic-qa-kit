# Suite trust session pack

Use when the question is whether a suite's verdicts can be trusted: flaky or order-dependent tests, retries, quarantine, hermeticity and entropy.

## Authority: fail closed

Local checks: rerunning tests in fresh processes with varied seeds, order or environment, in the target or a disposable copy.

Each of these needs its own approval:
- editing tests, CI configuration, retry settings or quarantine lists;
- installing test plugins, such as rerun or random-order ones;
- rerunning shared CI jobs or clearing their caches.

Never skip, retry away or quarantine a test to make a suite pass. A quarantine is an owner's recorded decision, not a session action. Without approval, record the attempt as `inconclusive` and stop.

## Suite and claim

Name the suite, command and revision, and the claim under test:
1. **Determinism:** the same inputs give the same verdict.
2. **Isolation:** a test's verdict does not depend on order or on other tests.
3. **Hermeticity:** the verdict depends only on declared inputs, not on network, clock, locale, hash seed, leftover files or ambient variables.
4. **Signal:** a failure means a defect, and no retry hides it.

## Environment

Record:
- runtime and flags;
- hash seed and random seeds;
- test selection and order;
- time zone, locale and clock;
- environment variables the suite reads;
- network, parallelism and temporary state before the run.

## Oracle

Rerun one test in fresh processes, varying one entropy source at a time: hash seed, order (alone, reversed), time zone or locale, parallelism. A verdict that changes with one source names that source. Then classify the cause:
- **product defect:** the code depends on entropy its contract excludes, such as set order when order is documented;
- **test defect:** shared state, unseeded randomness or a timing assumption;
- **environment:** a missing service or leftover file.

For a retry policy, report which observed failures it would hide.

## Uncertainty

- N passing runs do not rule out a flake. Report N, the sources varied and the failure rate.
- A failure reproduced under a fixed seed is deterministic. Record the seed.
- A source not varied is not evaluated.

## Stop conditions

Stop on any of these:
- an authorization boundary;
- continuing would need a fix;
- state leaking beyond the target;
- target drift;
- the charter budget.

## Evidence

Keep:
- exact commands and environment;
- seeds and order for every run;
- a per-run verdict table and first failure output;
- the minimized reproduction: one test, one seed;
- the classification and its basis.
