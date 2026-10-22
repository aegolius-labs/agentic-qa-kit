# Discovery contract

## Required output

Return a compact profile with:

1. Target identity: root, revision or `unknown`, dirty state, repository instructions.
2. Product context: intended use, users, critical journeys, boundaries, dependencies, sensitive data, environments.
3. Execution surface: languages, toolchains, canonical build/test/static commands, CI lanes, fixtures/services, UI/browser needs.
4. Existing evidence: what each test/analysis layer supports, its oracle, freshness, reproducibility, and material gaps.
5. Quality/risk profile: selected attributes, scenario, consequence, uncertainty, owner when known, and evidence needed.
6. Charter portfolio: ordered, bounded, independently checkable QA work.
7. Constraints and authorization: allowed, approval-required, forbidden, or unknown actions.
8. Open questions: only facts that cannot be discovered locally and would materially change the plan.

## Technique-routing questions

- Rules/ranges/states uncertain: use partitions, boundaries, decision tables, scenarios, or state models, recorded as charter obligations (qa-session's functional-design reference).
- API/schema/provider-consumer risk: inspect contracts and negative/compatibility behavior.
- Broad input space: consider properties, metamorphic relations, fuzzing, or constrained combinations.
- Weak suite sensitivity: consider mutation or differential evidence, not coverage alone.
- Change-focused request: inspect dependency/change facts, then choose conservative impacted tests plus mandatory gates.
- Timing/capacity risk: require a declared workload, environment, telemetry, and acceptance distribution.
- Failure/recovery risk: require a fault model, steady-state oracle, blast radius, rollback, and explicit authorization.
- UI/user risk: include accessibility tree, keyboard/assistive technology, locale, compatibility, and durable task outcomes.
- Persistence/migration risk: include invariants, concurrency, reconciliation, rollback/roll-forward, and data governance.
- AI/agent target: version the full configuration and test repeated outcomes, trajectories, side effects, policy, memory, recovery, and cost separately.

Do not select every technique. Choose the smallest portfolio that reduces the most decision-relevant uncertainty within the available budget.
