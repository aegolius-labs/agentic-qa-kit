# Evidence package

## Minimum session report

- Decision scope and exact target identity.
- Intended use, selected quality claims, risks, and applicable constraints.
- Included/excluded scope and environment.
- Methods and oracles.
- Attempt counts by outcome; retry and flake semantics.
- Findings by status and severity with direct evidence links.
- Coverage against declared charters or obligation ledgers, not a universal quality percentage.
- Evidence gaps, uncertainty, data completeness, and method limitations.
- Open defects, exceptions, compensating controls, owners, and expiry when known.
- Recommended disposition and next evidence action.

## Evidence review questions

1. Does the evidence address the actual claim and population?
2. Was the method executed validly against the identified target?
3. Is the oracle independent enough to detect the relevant fault?
4. Are all attempts, first failures, exclusions, and retries visible?
5. Can another competent person reproduce or audit the observation?
6. Are environment, tool, fixture/data, and configuration versions recorded?
7. Are privacy, sensitive-data, and retention constraints satisfied?
8. Is uncertainty explicit, including what cannot be concluded?

Hashes and immutable storage can show that bytes did not change; they do not prove that the source, method, or oracle was correct.
