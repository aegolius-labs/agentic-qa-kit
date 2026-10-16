# Agentic QA Kit Roadmap

Last updated: 2026-10-16

## Product goal

Create a host-portable QA plugin that can autonomously perform full or partial, risk-based quality workflows across diverse codebases while producing reproducible evidence and safe backlog handoffs. The repository remains the QA component of a broader agentic SDLC suite; backlog operations stay in `agentic-backlog-kit`.

Claude Code is the primary host and Codex is supported alongside it. `skills/` is the single source of truth for behavior on both; a per-host manifest carries only packaging and provenance. Skill content is never forked per host, and a host-specific divergence is recorded as a limitation rather than resolved by duplicating a skill.

## Progress rules

- Update the date and current checkpoint whenever a work item changes state.
- Mark a milestone complete only when every checked outcome has observable validation evidence.
- Use `Not started`, `In progress`, `Blocked`, or `Complete` on ranked work items; record the reason and next proof required.
- Keep completed work in place. Add newly discovered work with a stable ID instead of silently broadening an existing item.
- Mark an outcome `[x]` only when it was met. Use `[-]` for an outcome deliberately retired unmet, and state why and where it now lives. Never convert an unmet outcome into a completed one by narrowing it.
- A passing structural validator is necessary but not sufficient for behavioral completion.

## Architectural decisions

- The QA lifecycle is `context -> risk/claims -> discovery -> charters -> attempts -> findings -> reproduction -> evidence/report -> backlog handoff -> learning`.
- Full and partial workflows share the same session/evidence contract; each stage is independently invocable and resumable.
- Skills contain judgment and routing. A dependency-free local engine validates and stores compact manifests, sessions, attempts, findings, and backlog payloads.
- The engine does not execute tests or authorize effects. The host agent uses available tools under the target repository's permissions and records what actually happened.
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
- [x] Install and enable the plugin from the personal marketplace.
- [x] Add Claude Code as a first-class host: `.claude-plugin/plugin.json`, a marketplace entry, and manifest parity tests.
- [ ] Execute the tracked activation suite in fresh top-level tasks on the primary host lane and retain its observations.

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

- [x] Add clean-checkout Windows and Linux CI. CI runs on Linux, Windows and macOS with Python 3.11-3.14 (2026-10-14).
- [x] Run plugin and skill structural validation in CI. `scripts/validate_plugin.py` runs Claude Code's bundled validator and fails on any warning not documented in `CLAUDE.md` (2026-10-14).
- [x] Run installed-plugin behavioral evaluations with recorded artifacts. The Q01 Claude Code lane result is committed under `evals/results/` (2026-10-16).
- [x] Establish token/byte budgets for discovery, session summaries, and reports. `scripts/budgets.py --check` bounds skill text and resume output in bytes and runs in CI and release preflight (2026-10-16). Agent-written reports are measured per Q01 observation rather than budgeted.
- [x] Complete security, contribution, support, licensing, changelog, and release documentation: `SECURITY.md`, `CONTRIBUTING.md`, `SUPPORT.md`, `LICENSE.md` and `COMMERCIAL.md` (PolyForm Noncommercial 1.0.0, owner decision 2026-10-16), `CHANGELOG.md` and `docs/release.md`.
- [ ] Publish `0.1.0` with explicit limitations and evaluation evidence. The organization release workflow cuts it from this change's `feat:` merge once the `v0.0.0` baseline tag exists on `c0b1ccf`.

## Current checkpoint

Claude Code became a first-class host on 2026-09-16 (commit 4537d1f). Both host
manifests and `skills/` validate under Claude Code's bundled validator, manifest
parity is enforced by test, and the plugin installs and enables from a local
directory marketplace as `agentic-qa-kit@aegolius-labs-qa`. The unit suite is
green.

Q01 has been re-baselined onto a Claude Code primary lane. The Codex lane's
36 initial observations (24 pass, 4 fail, 8 inconclusive) and its 13-case
remediation rerun are retained as evidence and are not discarded: F01-F06 and
harness gaps G01-G02 have implementation and regression coverage, and 12 source
oracles were met. What the Codex lane could not establish was provenance, because
tasks created from an already-open parent inherited a stale installed-skill root.
Q01-G03 asked for a clean Codex top-level rerun and is retired unmet: it is a
property of that lane's execution, not a defect in the skills, and it held the
critical path for three weeks. The Claude Code lane cannot reproduce that failure
mode, because a directory marketplace resolves the install to the working tree.
That same property is the lane's standing limitation and is recorded on every
observation: the lane evidences the skills as written, not a published artifact.

The Claude Code lane ran all 36 cases on 2026-10-16: 34 pass and 2 fail, with
no inconclusive observation. Both failures were activation misses traced to skill
descriptions (Q01-F07), and the lane surfaced one unresolved authorization rule
(Q01-F08). The two activation misses are fixed and pass on rerun; Q01 closes
once Q01-F08 is decided.

Q09 is now the active item. The repository declares itself a QA target
(`.agentic-qa/manifest.json` is tracked; generated session evidence stays
ignored), which is the precondition for dogfooding. No self-QA session has been
run yet, so the kit has produced no evidence about itself. That run is the next
proof required.

## Ranked work items

### Q01 - Validate the installed plugin and activation boundaries

- **Status:** In progress
- **Importance:** Critical
- **Complexity:** Medium
- **Depends on:** M1 structural validation, M2 ledger tests
- **Approach:** Install through a local marketplace and run the 36 cases in evals/q01-activation-cases.json, following evals/README.md, across direct, indirect, incomplete, negative, follow-up, and authorization-sensitive prompts for all six skills. The suite runs as per-host lanes over one host-neutral case matrix. Claude Code is the primary lane and closes this item; Codex is tracked as a secondary lane under Q10 and does not gate Q02.
- **Done when:** On the Claude Code lane, expected skills activate, unrelated requests do not, bundled references resolve, partial workflows resume correctly, and no write occurs without the applicable authority. Closure is explicitly scoped to working-tree skill behavior, not released-artifact behavior.
- **Progress:**
  - [x] Install and enable agentic-qa-kit@personal.
  - [x] Add one case for every skill/category pair and validate the matrix contract.
  - [x] Retain one observation for every matrix case and publish the partial result (24 pass, 4 fail, 8 inconclusive). The Codex lane result stayed under the ignored `.agentic-qa/evaluations/q01/` and was never committed, so only its counts survive here.
  - [x] Execute all initial cases in fresh tasks and retain immutable transcript references.
  - [x] Q01-F01: Reproduce and correct dependency-install authority leakage in Q01-WF-DIRECT.
  - [x] Q01-F02: Resolve the unlisted qa-session companion activation in Q01-WF-FOLLOWUP.
  - [x] Q01-F03: Define an append-only continuation that can link new reproduction evidence to a terminal finding without replacing history.
  - [x] Q01-F04: Keep qa-report evidence review read-only when no linked completed session exists; do not install dependencies or generate a replacement session implicitly.
  - [x] Q01-F05: Fix completed session-close so unexecuted charters cannot be represented as completed, with zero-attempt and partial-execution regression coverage.
  - [x] Q01-G01: Add a safe authorization-case harness that permits exact prompt delivery while preventing consequential effects before plugin activation.
  - [x] Q01-G02: Provide disposable confirmed-finding, planning, backlog, and offline remote-snapshot fixtures for handoff cases.
  - [x] Preserve the focused remediation rerun, also local only (13 inconclusive by installed-version provenance; 12 source oracles met).
  - [x] Q01-F06: Prevent a continuation from persisting a replacement finding with its linked source finding ID.
  - [-] Q01-G03: Retired unmet. A clean Codex top-level installed-version rerun stays desirable but is a Codex-lane provenance concern, not a skill defect, and no longer gates this item. Tracked under Q10.
  - [x] Q01-G04: Define the Claude Code primary lane, its install procedure, its observation fields, and its standing working-tree provenance limitation in evals/README.md.
  - [x] Q01-G05: Install the plugin, then execute all 36 cases on the Claude Code lane from fresh top-level sessions, recording host, surface, and install location per observation. `scripts/q01_claude_code.py` runs the lane headlessly; [Claude Code lane result](evals/results/q01-claude-code-2026-10-16.json) (34 pass, 2 fail, CLI surface, 2026-10-16).
  - [ ] Triage Claude Code lane failures, rerun affected cases after fixes, and publish the Q01 lane result.
  - [x] Q01-F07: `qa-session` did not activate for Q01-SESS-INDIRECT and `qa-backlog-handoff` did not activate for Q01-HANDOFF-INCOMPLETE. Both descriptions now name the missed request; the [rerun](evals/results/q01-claude-code-2026-10-16-f07-rerun.json) passes both cases, their two negatives and two neighbouring cases (6 of 6, 2026-10-16).
  - [ ] Q01-G07: List the stage skills as allowed companions on the positive `qa-workflow` cases. `qa-workflow` is told to enter `qa-discover`, `qa-session`, `qa-reproduce` and `qa-report` as stages, so the judge's "unlisted skill" flag on those cases needs a reviewer every time.
  - [ ] Q01-F08: Decide whether a bounded concurrency probe in a disposable directory is `run_load_or_fault_injection`. Five lane runs ran one without asking and three asked first; the skills must state one rule.
  - [ ] Q01-G06: Exercise the desktop surface. The 2026-10-16 lane ran the headless CLI only.

### Q02 - Forward-test heterogeneous repositories

- **Status:** Not started
- **Importance:** Critical
- **Complexity:** Hard
- **Depends on:** Q01 Claude Code lane
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

### Q09 - Dogfood the kit on itself under Claude Code

- **Status:** In progress
- **Importance:** Critical
- **Complexity:** Medium
- **Depends on:** M1 Claude Code host support, M2 ledger
- **Approach:** Treat this repository as a QA target of itself. Track
  `.agentic-qa/manifest.json` with a real quality profile, keep generated session
  evidence ignored, and run the full lifecycle here: discovery, a bounded
  session, reproduction of anything found, an evidence package, and a handoff
  decision. Use the installed Claude Code plugin, not the working-tree files read
  as documents.
- **Done when:** At least one complete session exists whose attempts were
  actually executed against this repository, whose findings are classified
  honestly, and whose report states what the session did not establish. The kit's
  own defects found this way are dispositioned under the authority model: inside
  modeled intent they are `revert-node`, otherwise `bug-handoff`.
- **Rationale:** Until the kit produces evidence about itself, every claim in
  this roadmap about its behavior rests on unit tests and structural validators,
  which the progress rules already say are insufficient for behavioral
  completion. Dogfooding is also the cheapest source of Q02-shaped signal, since
  this repository is a real Python, no-integration-test, plugin-shaped target.
- **Progress:**
  - [x] Track a self-targeting `.agentic-qa/manifest.json` and narrow `.gitignore` so generated evidence stays untracked.
  - [x] Declare the quality profile Q09 evaluates against: functional suitability, data integrity, security, compatibility, and maintainability.
  - [x] Add regression coverage so the self-target cannot be silently ignored or drift out of contract.
  - [ ] Run `qa-discover` against this repository through the installed plugin and retain the profile and charters.
  - [ ] Execute at least one bounded session with real attempts and record them with `attempt-add`.
  - [ ] Produce an evidence package and a disposition, and record the limitations the session could not close.
  - [ ] Feed anything confirmed back into this roadmap as tracked work rather than an inline fix.
  - [x] Q09-F01: Concurrent writers to one session silently lost records; 16 parallel `attempt-add` calls all exited 0 and left 1 record. Every session write now holds an OS file lock, with a 12-writer regression test (2026-10-16).
  - [x] Q09-F02: `finding-update` could rewrite a confirmed finding's `actual`, `expected` and `recorded_at` and erase a candidate's evidence. History fields are now append-only and observation fields are fixed once a finding leaves `candidate` (2026-10-16).

### Q10 - Restore the Codex secondary lane

- **Status:** Not started
- **Importance:** Medium
- **Complexity:** Medium
- **Depends on:** Q01 Claude Code lane
- **Approach:** Re-run the Codex lane from genuinely new top-level tasks against
  an install whose resolved skill root is verified before the first case, so
  observations carry provenance. Retain the existing Codex evidence; do not
  restart the matrix from zero.
- **Done when:** Codex lane observations are conclusive on provenance and their
  per-case outcomes are comparable to the Claude Code lane. Divergence between
  hosts is recorded as a limitation, never resolved by forking a skill.
- **Note:** This item exists so that de-gating Q02 does not quietly become
  dropping Codex support. Codex remains a supported host.

## Dependency and execution waves

| Wave | Work | Parallelism | Exit gate |
| --- | --- | --- | --- |
| A | M1 scaffold + M2 ledger + core skill contracts | Ledger/tests can proceed beside skill writing after contracts freeze | Unit tests and structural validators green |
| B | Q01 Claude Code activation lane + Q09 self-dogfooding + Q02 fixture preparation + Q06 interoperability preparation | Four isolated evaluation lanes; Q09 shares the Claude Code install with Q01 | Recorded behavioral evidence and issue list |
| C | Q03 evidence chaining + Q04 design pack + Q05 NFR packs | Isolated branches with shared schema review | Migration tests and technique-specific evals |
| D | M5 shift-right/fleet learning + Q07 MCP decision + Q10 Codex lane restoration | Decision work can run beside non-production simulations; the Codex lane is independent | Production authority model, MCP decision record, and comparable per-host lane outcomes |
| E | Q08 agentic assurance + release hardening | Agentic evals beside CI/docs/benchmarks | Release packet with limitations and residual risks |

Critical path:

```text
M1/M2 foundation -> Q01 Claude Code activation lane -> Q09 self-dogfooding
    -> Q02 heterogeneous evaluation -> Q03/Q04/Q05 capability expansion
    -> M5/M6 assurance -> M7 release

Q10 (Codex lane) runs off the critical path and rejoins before M7 release.
```
