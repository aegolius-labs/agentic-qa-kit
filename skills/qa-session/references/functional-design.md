# Functional test design

Use when a charter checks specified behavior: rules, ranges, states or flows.

## Pick the technique from the specification

| Specification shape | Technique | One obligation per |
| --- | --- | --- |
| Input or output classes | `partition` | valid and invalid class |
| Ordered ranges, limits, sizes | `boundary` | each side of each edge |
| Conditions combining into actions | `decision-table` | feasible rule |
| Modes, lifecycles, protocols | `state-transition` | allowed transition and one forbidden one per state |
| User or system journeys | `scenario` | main flow and each exception |
| Many interacting parameters | `combinatorial` | required interaction (pairwise unless risk says higher) |
| General relations, round-trips | `property` | stated invariant |

Take only the techniques the specification's shape calls for.

## Write the obligation ledger before running anything

Record each obligation in the charter's `obligations`:
- `id`;
- `technique`;
- `source`: the line of the spec, doc or code comment it comes from;
- `statement`: the case;
- `oracle`: the expected result, worked out independently of the code under test.

When the specification is silent or ambiguous, write the obligation down anyway and record the ambiguity as a gap. Never settle the ambiguity by reading the implementation.

## Execute and link

- Link each attempt to the obligations it exercised with `obligation_ids`.
- Prefer existing tests that already exercise an obligation. Write a new probe only within the charter's authority.
- Record each obligation's result as observed. A pass and a fail both count as exercised; `inconclusive` and `error` do not.

## Oracle independence

An oracle may come from:
- a spec value;
- a hand calculation;
- a reference implementation;
- a metamorphic relation.

It must not come from the code under test or from a snapshot of it. Say which one each oracle is.

## Claims

`summary` reports obligation coverage as total, exercised, inconclusive and unexercised. That measures coverage of this model of the specification only. Report it as such. Never present it as defect absence, as code coverage, or as coverage of anything the model omits. Name unexercised obligations and their reasons in the report.
