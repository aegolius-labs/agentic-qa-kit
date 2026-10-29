# Resilience and recovery session pack

Use when a charter's quality attribute is `reliability`: fault tolerance, degradation, recovery, backup and restore.

## Authority: fail closed

Inject faults only into processes, containers or data the session created and can discard. Each of these needs its own approval naming the target, blast radius, abort trigger and rollback:
- killing, pausing or partitioning anything shared;
- corrupting or deleting data;
- changing clocks, quotas or network rules on the host;
- touching a backup;
- any fault in staging or production.

If the rollback is unknown, do not inject. Record the attempt as `inconclusive` and stop.

## Fault model

State the hypothesis first, for example: "losing the cache keeps writes durable and recovers within 30 s." Then name:
- the single fault injected, such as process loss, dependency error or delay, duplicate or reordered message, storage full or read-only, clock skew, or a restore from a backup;
- where it is injected;
- what is held constant.

Inject one fault at a time.

## Environment

Record:
- revision and configuration;
- topology: processes, replicas and dependencies, with their versions;
- data seed and state before the fault;
- the health check used for "recovered".

Take a baseline window before the fault.

## Oracle

"It responds again" is not recovery. The oracle covers both delivered capability and correctness:
- acknowledged writes are preserved, with no duplicates or lost updates;
- ordering and authorization still hold;
- business invariants are checked after recovery;
- time to recover is measured from the fault trigger to that validated state.

Compare against the stated RTO, RPO or degradation bound. When none is specified, record the gap and report what was observed.

## Uncertainty

- One injection shows that a path exists, not how often it happens.
- Easy faults may not be representative. Name faults not tried.
- Retries can hide an error or amplify load. Count them.
- A single-node local pass says nothing about shared-cause failures across zones or providers.

## Stop conditions

Stop on any of these:
- the declared abort trigger;
- loss of the ability to roll back;
- effects outside the declared blast radius;
- data corruption outside the fixture;
- target drift;
- reaching an authorization boundary;
- the charter budget.

After an abort, roll back and verify the rollback first.

## Evidence

Keep:
- the hypothesis;
- the exact injection command;
- timestamps for fault, detection and recovery;
- baseline and post-recovery checks, with invariant results;
- logs around the fault;
- the rollback record.
