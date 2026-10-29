# Data integrity session pack

Use when a charter's quality attribute is `data-integrity`: validity, keys and references, invariants, paging, concurrency, persistence, events, pipelines and migrations.

## Authority: fail closed

Work only on data the session created or a disposable copy: a temporary database, file or fixture. Each of these needs its own approval:
- reading real or personal data;
- writing to a shared, staging or production store;
- running a migration outside a disposable copy;
- replaying events into a live consumer.

Without approval, record the attempt as `inconclusive` and stop.

## Population and claim

Name the dataset, table, stream or batch and window, and the claim under test; each needs its own oracle:
1. **Validity:** types, nulls, ranges and formats.
2. **Structure:** keys, uniqueness, references and cardinality.
3. **Semantics:** business invariants and what each transformation means.
4. **Persistence:** committed state survives crash, retry and concurrency without loss, tear, reordering or duplication.

## Environment

Record:
- revision;
- engine and driver versions;
- isolation level and retry policy;
- schema version;
- data seed or input digest;
- any clock or time-zone dependency.

## Oracle

- **Concurrency:** force the interleaving (same-key insert, double spend, read-modify-write, parent delete during child insert), then check the final state against the invariant, not a call count.
- **Events:** check the final effect after duplicate, out-of-order, poison and replayed events, and after a crash around acknowledgment.
- **Pipelines:** source = loaded + rejected + quarantined + excluded, plus keyed comparison and canonical row digests. Counts alone can match after a key swap.
- **Migrations:** the stated mapping holds for every record class. Verify rollback, or state the mapping is lossy.

## Uncertainty

- An isolation level's name does not define behavior; the configured engine does.
- A race absent in N runs is not ruled out. Report N and how it was forced.
- A sample does not cover the full population.
- A schema check proves shape, not meaning.

## Stop conditions

Stop on any of these:
- an authorization boundary;
- any write that escapes the disposable copy;
- real or personal data appearing in output;
- target drift;
- the charter budget.

## Evidence

Keep:
- exact commands and scripts;
- the schema and engine record;
- input and output digests;
- the operation history for each forced interleaving;
- invariant query results;
- reconciliation counts and differences.

Never copy real or production rows into evidence.
