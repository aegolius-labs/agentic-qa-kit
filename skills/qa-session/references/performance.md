# Performance session pack

Use when a charter's quality attribute is `performance-efficiency`: latency, throughput, resource use or capacity.

## Authority: fail closed

Without explicit approval for that run, generate no load against anything except a disposable local process the session started itself. Shared, staging, production, rate-limited or paid targets each need their own approval, naming the target, peak rate, duration and abort ceiling. If any of these is missing, record the attempt as `inconclusive` and stop.

## Workload

Write it down before measuring:
- the boundary measured, from client edge to the named component;
- the operation mix, payload and data sizes;
- open arrivals (fixed rate) or closed users (concurrency plus think time), chosen from how real demand arrives;
- warmup, duration and repetitions.

A closed generator lowers its own load when the target slows. Prefer an open one when the question is about tails. Record offered and achieved load.

## Environment

Pin and record:
- revision, runtime and flags;
- OS, CPU and memory, and whether the host is shared;
- data seed and cache state, cold or warm;
- the generator's own CPU.

A saturated generator measures itself. A shared or noisy host makes the result `inconclusive` for any threshold closer than the observed run-to-run spread.

## Oracle

Use a stated threshold or a comparison against a baseline measured in the same environment, never a number recalled from elsewhere. Judge throughput, tail latency, error and timeout rate, and resource headroom together. A mean alone is not an oracle. When no threshold is specified, report the measurements and record the missing threshold as a gap rather than inventing one.

## Uncertainty

- Report sample count and the spread across repetitions.
- A p99 from a few hundred samples, or from a single run, is an estimate. Label it as one.
- Treat a difference smaller than the run-to-run spread as no observed difference.
- Never extrapolate capacity beyond the largest load actually offered.

## Stop conditions

Stop on any of these:
- the error rate or latency ceiling declared before the run;
- resource exhaustion on the host;
- generator saturation;
- target drift;
- reaching an authorization boundary;
- the charter budget.

## Evidence

Keep:
- the exact command and generator configuration;
- the environment record;
- raw latency samples or histograms;
- offered and achieved load, errors, and resource readings.

Store large raw output as evidence files, so their digests seal them. Summaries go in the attempt record.
