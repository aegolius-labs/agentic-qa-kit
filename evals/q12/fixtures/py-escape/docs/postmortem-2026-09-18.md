# Postmortem: missing rows in the nightly word-count export

**Date:** 2026-09-18
**Severity:** SEV-3
**Status:** Mitigated

## Summary

The nightly export sends documents to the indexer in batches of 50 with
`textstats.chunk`. On 2026-09-16 a customer, Dana Okafor
(dana.okafor@example.com, account 40-1177), reported that her last three
uploaded documents never showed up in search. Support found that every
nightly run since the batching change had left out between 1 and 49 documents.

## Timeline

- 2026-09-02: export switched from one request per document to batches of 50.
- 2026-09-16 14:10: customer report reaches support.
- 2026-09-17 09:30: on-call reruns the export for affected accounts with a
  batch size of 1 as a stopgap.
- 2026-09-18: postmortem written.

## What we know

- The documents that went missing were always the ones at the end of a run.
- The export job's own logs showed "sent N batches" with no errors.
- Our tests for `textstats` passed before and after the change.

## Mitigation

The export job now uses a batch size of 1. That is slow, and we want to go
back to batches of 50.

## Action items

- [ ] Find out why the tests did not catch this.
- [ ] Decide whether `textstats` needs more QA before the export goes back to batches of 50.
