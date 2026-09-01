# Agentic QA Kit Roadmap

Last updated: 2026-08-31

## Product goal

Create a Codex-first QA plugin that can autonomously perform full or partial, risk-based quality workflows across diverse codebases while producing reproducible evidence and safe backlog handoffs. The repository remains the QA component of a broader agentic SDLC suite; backlog operations stay in `agentic-backlog-kit`.

## Progress rules

- Update the date and current checkpoint whenever a work item changes state.
- Mark a milestone complete only when every checked outcome has observable validation evidence.
- Use `Not started`, `In progress`, `Blocked`, or `Complete` on ranked work items; record the reason and next proof required.
- Keep completed work in place. Add newly discovered work with a stable ID instead of silently broadening an existing item.
- A passing structural validator is necessary but not sufficient for behavioral completion.

## Architectural decisions

- The QA lifecycle is `context -> risk/claims -> discovery -> charters -> attempts -> findings -> reproduction -> evidence/report -> backlog handoff -> learning`.
- Full and partial workflows share the same session/evidence contract; each stage is independently invocable and resumable.
- Skills contain judgment and routing. A dependency-free local engine validates and stores compact manifests, sessions, attempts, findings, and backlog payloads.
- The engine does not execute tests or authorize effects. Codex uses available tools under the target repository's permissions and records what actually happened.
- Agent output is a proposal until supported by an independent oracle. Objective checks outrank model judgment.
- Session evidence binds the target revision, environment, method, oracle, attempts, limitations, and disposition.
- Discovery is read-only by default. Writes, destructive operations, production exposure, sensitive data, external messages, and unbounded cost require explicit authorization.
- No MCP server is planned until evaluations demonstrate a missing controlled capability or an unacceptable tool/context cost.
- Backlog handoff produces a confirmed Bug payload only. Agentic Backlog Kit owns planning and synchronization.

## Milestones

### M0 - Research and product boundary

- [x] Extract the quality control loop, evidence model, autonomy controls, and maturity path from `Modern_Quality_Engineering_2026.md`.
- [x] Define the separation between QA evidence production and backlog management.
- [x] Inventory full and partial QA use cases.

### M1 - Installable plugin foundation

- [x] Create the private aegolius-labs/agentic-qa-kit GitHub repository and establish main with the validated foundation.
- [x] Create and validate the `.codex-plugin/plugin.json` shape.
- [x] Add focused skills for orchestration, discovery, sessions, reproduction, reporting, and backlog handoff.
- [x] Add UI metadata and concise starter prompts.
- [ ] Install from a local marketplace and evaluate skill activation in a fresh Codex task.

### M2 - Deterministic evidence ledger

- [x] Define versioned manifest, session, attempt, finding, and handoff contracts.
- [x] Implement dependency-free initialization, validation, append, summary, show, close, and export commands.
- [x] Reject duplicate identities, invalid transitions, unconfirmed exports, missing evidence, and incomplete planning inputs.
- [x] Add unit tests for validation, lifecycle behavior, and safe handoff generation.
- [ ] Add content digests and optional append-only receipt chaining for consequential evidence.

### M3 - Autonomous core QA workflow

- [x] Define read-only discovery and risk-to-charter planning.
- [x] Define bounded session execution with attempt-level recording and explicit stop conditions.
- [x] Define controlled reproduction and minimization with honest inconclusive outcomes.
- [x] Define evidence/package and backlog handoff workflows.
- [ ] Forward-test all six skills against representative Python, JavaScript/TypeScript, compiled, monorepo, and no-test codebases.
- [ ] Add evaluation cases for dirty worktrees, missing runtimes, flaky tests, generated code, external services, and permission denial.

### M4 - Technique and quality-attribute packs

- [ ] Add specification/model-based design guidance: partitions, boundaries, decision tables, states, and oracle design.
- [ ] Add static, contract, property, metamorphic, mutation, and adequacy routing.
- [ ] Add performance/capacity, reliability/recovery, accessibility/compatibility/i18n, and data-integrity session packs.
- [ ] Integrate with a dedicated security workflow when available instead of duplicating specialist security tooling.
- [ ] Add test-data privacy, representativeness, retention, and disposal controls.

### M5 - CI, shift-right, and fleet learning

- [ ] Add hermetic environment, fixture, entropy, retry, quarantine, and suite-trust evidence.
- [ ] Add observability-contract and diagnosability verification.
- [ ] Add progressive-delivery, synthetic, shadow, and field-feedback session modes with explicit production authorization.
- [ ] Feed confirmed escapes and incident evidence back into discovery models and regression charters.
- [ ] Define cross-session metrics with denominators, uncertainty, anti-gaming guardrails, and no individual ranking.

### M6 - AI and agentic-system QA

- [ ] Add nondeterministic-system evaluation contracts for configurations, estimands, repeats, judges, uncertainty, and drift.
- [ ] Add trajectory, state, artifact, tool-policy, memory, handoff, and multi-agent oracles.
- [ ] Add resettable simulations, capability-broker checks, hidden scenario families, and repeated pass-consistency measures.
- [ ] Validate external kill, rollback, budget, and human-takeover behavior.

### M7 - Release readiness

- [ ] Add clean-checkout Windows and Linux CI.
- [ ] Run plugin and skill structural validation in CI.
- [ ] Run installed-plugin behavioral evaluations with recorded artifacts.
- [ ] Establish token/byte budgets for discovery, session summaries, and reports.
- [ ] Complete security, contribution, support, licensing, changelog, and release documentation.
- [ ] Publish `0.1.0` with explicit limitations and evaluation evidence.

## Current checkpoint

Foundation implementation completed on 2026-08-27 and was pushed to the private aegolius-labs/agentic-qa-kit GitHub repository on 2026-08-31. The plugin manifest and all six skills pass the bundled Codex validators; 14 local unit tests pass; and a disposable CLI smoke run completed initialization, session creation, attempt recording, confirmed-finding recording, summary, backlog export, closeout, and whole-ledger validation. The next gate is Q01 installed-plugin behavioral evaluation, followed by Q02 heterogeneous-repository forward tests. Deeper technique packs and production/agentic assurance remain intentionally open.

## Ranked work items

### Q01 - Validate the installed plugin and activation boundaries

- **Status:** Not started
- **Importance:** Critical
- **Complexity:** Medium
- **Depends on:** M1 structural validation, M2 ledger tests
- **Approach:** Install through a local marketplace and run direct, indirect, incomplete, negative, follow-up, and authorization-sensitive prompts for all six skills.
- **Done when:** Expected skills activate, unrelated requests do not, bundled references resolve, partial workflows resume correctly, and no write occurs without the applicable authority.

### Q02 - Forward-test heterogeneous repositories

- **Status:** Not started
- **Importance:** Critical
- **Complexity:** Hard
- **Depends on:** Q01
- **Approach:** Use disposable fixtures representing Python, TypeScript, compiled, monorepo, UI, service, and no-test projects. Preserve raw session artifacts and compare behavior against evidence contracts.
- **Done when:** Discovery and core sessions complete or stop honestly on every fixture, with no invented commands, runtimes, or verdicts.

### Q03 - Add chained evidence receipts

- **Status:** Not started
- **Importance:** High
- **Complexity:** Medium
- **Depends on:** Stable M2 contract
- **Approach:** Canonicalize records, hash each accepted mutation, and retain prior/current digests without claiming that hashes prove source truth.
- **Done when:** Tampering and missing links are detected, ordinary summaries remain compact, and migration from schema version 1 is tested.

### Q04 - Add model-based functional design pack

- **Status:** Not started
- **Importance:** High
- **Complexity:** Medium
- **Depends on:** Q02 findings
- **Approach:** Encode technique selection and evidence requirements for partitions, boundaries, rules, states, scenarios, combinatorial coverage, and independent oracles.
- **Done when:** Representative specifications produce reviewable obligation ledgers and tests without presenting model coverage as defect absence.

### Q05 - Add non-functional session packs

- **Status:** Not started
- **Importance:** High
- **Complexity:** Hard
- **Depends on:** Q02, authorization policy evaluation
- **Approach:** Add separate packs for performance, resilience/recovery, accessibility/compatibility/i18n, and data integrity; keep security integration separate.
- **Done when:** Every pack states workload/threat/population, environment, oracle, uncertainty, stop conditions, and evidence; risky effects fail closed.

### Q06 - Evaluate backlog-kit interoperability

- **Status:** Not started
- **Importance:** High
- **Complexity:** Medium
- **Depends on:** Stable Agentic Backlog Kit ingestion contract
- **Approach:** Export confirmed findings, validate them with the sibling kit, ingest only after explicit request, and prove QA evidence remains linked without duplicating backlog state.
- **Done when:** Confirmed findings become valid Bug items, candidates are rejected, missing business inputs are never guessed, and synchronization remains outside this plugin.

### Q07 - Decide whether to build an MCP server

- **Status:** Not started
- **Importance:** Conditional
- **Complexity:** Hard
- **Depends on:** Q01, Q02, token/call measurements
- **Approach:** Measure whether host tools plus the local ledger leave authorization, compact-query, portability, or structured-result gaps.
- **Done when:** Evidence supports either retaining the skills-only architecture or building a narrowly scoped server with explicit tools and permissions.

### Q08 - Agentic-system assurance pack

- **Status:** Not started
- **Importance:** Later
- **Complexity:** Hard
- **Depends on:** M4/M5 contracts, Q07 decision
- **Approach:** Test complete trajectories, side effects, policy decisions, memory, multi-agent handoffs, recovery, consistency, and budgets in resettable environments.
- **Done when:** Utility, safety, authorization, confidentiality, recovery, and cost are independently measured and critical invariant breaches cannot be averaged away.

## Dependency and execution waves

| Wave | Work | Parallelism | Exit gate |
| --- | --- | --- | --- |
| A | M1 scaffold + M2 ledger + core skill contracts | Ledger/tests can proceed beside skill writing after contracts freeze | Unit tests and structural validators green |
| B | Q01 installed evaluation + Q02 fixture preparation + Q06 interoperability preparation | Three isolated evaluation lanes | Recorded behavioral evidence and issue list |
| C | Q03 evidence chaining + Q04 design pack + Q05 NFR packs | Isolated branches with shared schema review | Migration tests and technique-specific evals |
| D | M5 shift-right/fleet learning + Q07 MCP decision | Decision work can run beside non-production simulations | Production authority model and MCP decision record |
| E | Q08 agentic assurance + release hardening | Agentic evals beside CI/docs/benchmarks | Release packet with limitations and residual risks |

Critical path:

```text
M1/M2 foundation -> Q01 installed evaluation -> Q02 heterogeneous evaluation
    -> Q03/Q04/Q05 capability expansion -> M5/M6 assurance -> M7 release
```
