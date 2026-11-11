# Agentic QA Kit Roadmap

Last updated: 2026-11-11

## Product goal

Create a host-portable QA plugin that can autonomously perform full or partial, risk-based quality workflows across diverse codebases while producing reproducible evidence and safe backlog handoffs. The repository is the QA component of the Aegolius Labs suite, whose end product is the `aio-agentic-sdlc` framework: the kit closes that framework's loop by returning evidence about reality, and it stays usable on its own. Backlog operations stay in `agentic-backlog-kit`.

Claude Code, Codex and Antigravity are equally supported hosts (owner decision, 2026-11-02, in the organization's CONTRIBUTING.md). Claude Code is the lane the evaluations run on, Codex has a manifest and less evidence (Q10), and Antigravity has no manifest yet (Q16). `skills/` is the single source of truth for behavior on every host; a per-host manifest carries only packaging and provenance. Skill content is never forked per host, and a host-specific divergence is recorded as a limitation rather than resolved by duplicating a skill.

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
- Composed with `aio-agentic-sdlc`, the framework chooses whether a finding reopens an Intention node (`revert-node`) or becomes a Bug (`bug-handoff`), and records that choice (owner decision, 2026-11-11). This kit supplies the evidence and does not choose. Standalone, `bug-handoff` is the only disposition.

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
- [x] Add content digests and optional append-only receipt chaining for consequential evidence. Every session write is sealed in a SHA-256 receipt chain (Q03, 2026-10-22); chaining is optional in that schema-version-1 sessions stay valid until migrated. Evidence files inside the repository are digested at write time and re-checked by `validate` (Q03-G01, 2026-10-22).

### M3 - Autonomous core QA workflow

- [x] Define read-only discovery and risk-to-charter planning.
- [x] Define bounded session execution with attempt-level recording and explicit stop conditions.
- [x] Define controlled reproduction and minimization with honest inconclusive outcomes.
- [x] Define evidence/package and backlog handoff workflows.
- [ ] Forward-test all six skills against representative Python, JavaScript/TypeScript, compiled, monorepo, and no-test codebases. Q02 (2026-10-22) covered discovery and core sessions through `qa-workflow`. `qa-reproduce`, `qa-report` and `qa-backlog-handoff` were not each invoked on every fixture.
- [ ] Add evaluation cases for dirty worktrees, missing runtimes, flaky tests, generated code, external services, and permission denial.

### M4 - Technique and quality-attribute packs

- [x] Add specification/model-based design guidance: partitions, boundaries, decision tables, states, and oracle design. `qa-session`'s functional-design reference and charter obligations (Q04, 2026-10-22).
- [ ] Add static, contract, property, metamorphic, mutation, and adequacy routing.
- [x] Add performance/capacity, reliability/recovery, accessibility/compatibility/i18n, and data-integrity session packs. `qa-session` references (Q05, 2026-10-27).
- [ ] Integrate with a dedicated security workflow when available instead of duplicating specialist security tooling.
- [ ] Add test-data privacy, representativeness, retention, and disposal controls.

### M5 - CI, shift-right, and fleet learning

- [x] Add hermetic environment, fixture, entropy, retry, quarantine, and suite-trust evidence. `qa-session`'s suite-trust reference (Q11, 2026-10-29).
- [x] Add observability-contract and diagnosability verification. `qa-session`'s observability reference (Q13, 2026-11-01).
- [x] Add progressive-delivery, synthetic, shadow, and field-feedback session modes with explicit production authorization. Ledger modes with a recorded, expiring `production_authorization` and `qa-session` guidance (Q14, 2026-11-02; owner decision the same day).
- [x] Feed confirmed escapes and incident evidence back into discovery models and regression charters. `qa-discover`'s escapes reference (Q12, 2026-10-29).
- [x] Define cross-session metrics with denominators, uncertainty, anti-gaming guardrails, and no individual ranking. `qa.py metrics` and `qa-report` routing (Q15, 2026-11-02).

### M6 - AI and agentic-system QA

- [ ] Add nondeterministic-system evaluation contracts for configurations, estimands, repeats, judges, uncertainty, and drift. Started with Q08 slice 1 (2026-11-05): trial attempts with seeds and per-dimension verdicts, critical flags, and a `trials` report; estimands, judges and drift remain.
- [ ] Add trajectory, state, artifact, tool-policy, memory, handoff, and multi-agent oracles. Started with Q08-G04 (2026-11-05): state and trajectory oracles in the `agentic-oracles` reference.
- [ ] Add resettable simulations, capability-broker checks, hidden scenario families, and repeated pass-consistency measures. Started with Q08 slice 1: the qa-session agentic-systems pack runs seeded trials in a sandbox reset before each one, against the py-agent fixture.
- [x] Validate external kill, rollback, budget, and human-takeover behavior. Kill, budget and handoff to a person are covered by Q08's `control` and `cost` dimensions (Q08-G03, 2026-11-05); rollback of partial side effects by the `agentic-oracles` reference and lane (Q08-G04, 2026-11-05).

### M7 - Release readiness

- [x] Add clean-checkout Windows and Linux CI. CI runs on Linux, Windows and macOS with Python 3.11-3.14 (2026-10-14).
- [x] Run plugin and skill structural validation in CI. `scripts/validate_plugin.py` runs Claude Code's bundled validator and fails on any warning not documented in `CLAUDE.md` (2026-10-14).
- [x] Run installed-plugin behavioral evaluations with recorded artifacts. The Q01 Claude Code lane result is committed under `evals/results/` (2026-10-16).
- [x] Establish token/byte budgets for discovery, session summaries, and reports. `scripts/budgets.py --check` bounds skill text and resume output in bytes and runs in CI and release preflight (2026-10-16). Agent-written reports are measured per Q01 observation rather than budgeted.
- [x] Complete security, contribution, support, licensing, changelog, and release documentation: `SECURITY.md`, `CONTRIBUTING.md`, `SUPPORT.md`, `LICENSE.md` and `COMMERCIAL.md` (PolyForm Noncommercial 1.0.0, owner decision 2026-10-16), `CHANGELOG.md` and `docs/release.md`.
- [x] Publish `0.1.0` with explicit limitations and evaluation evidence. The organization release workflow published the immutable [v0.1.0 release](https://github.com/aegolius-labs/agentic-qa-kit/releases/tag/v0.1.0) with its wheel and sdist from the `v0.0.0` baseline on `c0b1ccf` (2026-10-19).

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
(Q01-F08). The two activation misses are fixed and pass on rerun, and the owner
decided Q01-F08 on 2026-10-19, so Q01 meets its done-when. The desktop surface
(Q01-G06) and the judge's companion-skill list (Q01-G07) remain as follow-ups.

Q09 met its done-when on 2026-10-16. Two self-QA sessions ran through the
installed plugin (see the [Q09 report](docs/q09-self-qa-2026-10-16.md)). They
found a critical lost-update defect in the ledger and a history-rewrite defect,
and both are fixed. The owner decided Q09-F04 and Q09-F05 on 2026-10-22, and both are fixed.

0.1.0 was published on 2026-10-19 and M7 is complete.

Q02 met its done-when on 2026-10-22 on the Claude Code CLI lane. Eight
synthetic fixtures (Python, TypeScript, Go, monorepo, static UI,
database-backed service, no tests, and a missing .NET runtime) each got one
fresh session. All 8 completed or stopped honestly. Every planted defect was
found, and no command, runtime or verdict was invented. The run surfaced one
ledger-chaining hazard (Q02-F01) and a measured payload-discovery cost for Q07
(Q02-O01). Q03, Q04 and Q05 are next on the critical path.

## Ranked work items

### Q01 - Validate the installed plugin and activation boundaries

- **Status:** Complete for its done-when; follow-up items remain open
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
  - [x] Triage Claude Code lane failures, rerun affected cases after fixes, and publish the Q01 lane result. Both failures are Q01-F07, fixed and rerun.
  - [x] Q01-F07: `qa-session` did not activate for Q01-SESS-INDIRECT and `qa-backlog-handoff` did not activate for Q01-HANDOFF-INCOMPLETE. Both descriptions now name the missed request; the [rerun](evals/results/q01-claude-code-2026-10-16-f07-rerun.json) passes both cases, their two negatives and two neighbouring cases (6 of 6, 2026-10-16).
  - [x] Q01-G07: List the stage skills as allowed companions on the positive `qa-workflow` cases. `qa-workflow` is told to enter `qa-discover`, `qa-session`, `qa-reproduce` and `qa-report` as stages, so the judge's "unlisted skill" flag on those cases needed a reviewer every time. The five positive cases now list those four, `qa-backlog-handoff` stays unlisted because no case has a confirmed defect, and a matrix test pins it (2026-10-22).
  - [x] Q01-F08: Decide whether a bounded concurrency probe in a disposable directory is `run_load_or_fault_injection`. Five lane runs ran one without asking and three asked first. Owner decision (2026-10-19): it is a local check and needs no approval. `qa-session`, `qa-reproduce` and `docs/contracts.md` state the rule.
  - [ ] Q01-G06: Exercise the desktop surface. The 2026-10-16 lane ran the headless CLI only.

### Q02 - Forward-test heterogeneous repositories

- **Status:** Complete for its done-when on the Claude Code CLI lane; follow-up items remain open
- **Importance:** Critical
- **Complexity:** Hard
- **Depends on:** Q01 Claude Code lane
- **Approach:** Use disposable fixtures representing Python, TypeScript, compiled, monorepo, UI, service, and no-test projects. Preserve raw session artifacts and compare behavior against evidence contracts.
- **Done when:** Discovery and core sessions complete or stop honestly on every fixture, with no invented commands, runtimes, or verdicts.
- **Progress:**
  - [x] Q02-G01: Build disposable fixtures for Python, TypeScript, compiled, monorepo, UI, service, no-test and missing-runtime projects, each with planted defects and traps, keeping the oracle out of the staged target (`evals/q02/fixtures/`, `evals/q02-fixtures.json`).
  - [x] Q02-G02: Run the fixtures headlessly on the Claude Code lane and judge the done-when mechanically (`scripts/q02_claude_code.py`, procedure in `evals/README.md`).
  - [x] Run every fixture and publish the reviewed result: [Q02 Claude Code lane result](evals/results/q02-claude-code-2026-10-22.json). All 8 pass after review. All 11 planted defects were found, 9 of them confirmed. No command, runtime or verdict was invented, and nothing was installed (2026-10-22, plugin `9b1986c`, USD 4.60).
  - [x] Q02-F01: A rejected ledger write chained with `;` to `session-close` closed a session without its findings (smoke run of `dotnet-missing`). `qa-session` now requires each ledger write's exit status to be checked before the next, and `qa-report` forbids closing after a rejected write (2026-10-22). The skill text is the fix. It has not been rerun, because the failure happened once in nine runs.
  - [ ] Q02-O01: Every run read the plugin's `src/` or `examples/` and called `--help` to learn payload shapes. Carry that measurement into Q07, and decide whether the skills should give compact payload shapes.
  - [ ] Q02-G03: Repeat runs, and dirty-worktree, flaky-test, generated-code and permission-denial cases beyond the single dirty fixture, belong to M3's evaluation-case item. One run per fixture shows that a behavior can occur, not how often it does.

### Q03 - Add chained evidence receipts

- **Status:** Complete for its done-when; follow-up items remain open
- **Importance:** High
- **Complexity:** Medium
- **Depends on:** Stable M2 contract
- **Approach:** Canonicalize records, hash each accepted mutation, and retain prior/current digests without claiming that hashes prove source truth.
- **Done when:** Tampering and missing links are detected, ordinary summaries remain compact, and migration from schema version 1 is tested.
- **Progress:**
  - [x] Canonical JSON digests, and one linked receipt per accepted write in schema-version-2 sessions (`src/agentic_qa_kit/receipts.py`).
  - [x] Detect an edit made outside the ledger, an altered, removed or reordered receipt, and a dropped last write. A broken session refuses further writes and fails `validate` (`tests/test_receipts.py`).
  - [x] Keep summaries compact. `summary` adds one `integrity` field, and `show` replaces the chain with its status and count. Byte budgets are unchanged and pass.
  - [x] Migrate from schema version 1. Version-1 sessions stay valid and `unchained`, and `aqk migrate` seals one without changing its content. Tested, including on a terminal session.
  - [x] State the limits in `docs/contracts.md`. The chain does not authenticate a writer. It is no defense against someone who rewrites every receipt, or rolls the session back to an earlier sealed state; a test pins that last limit.
  - [x] Q03-G01: Digest the evidence files that attempts and findings reference, so a changed or replaced evidence file is detected. Done 2026-10-22: writes digest repository files and refuse a mismatched supplied digest; `validate` fails on a changed file and counts missing ones.
  - [ ] Q03-G02: Exercise receipts through the installed plugin (a Q01 or Q09 rerun) so the skills' use of `summary`, `show` and `validate` is observed with the new fields.

### Q04 - Add model-based functional design pack

- **Status:** Complete for its done-when (2026-10-27). The design pack and obligation ledger shipped in 0.4.0; Q04-G01 ran three representative specifications through the installed plugin and every session found its planted defects, recorded a reviewable ledger once the examples showed one, and made no defect-absence claim
- **Importance:** High
- **Complexity:** Medium
- **Depends on:** Q02 findings
- **Approach:** Encode technique selection and evidence requirements for partitions, boundaries, rules, states, scenarios, combinatorial coverage, and independent oracles.
- **Done when:** Representative specifications produce reviewable obligation ledgers and tests without presenting model coverage as defect absence.
- **Follow-ups:**
  - [x] Q04-G01: Run representative specifications through the installed plugin (Q02 fixtures with written rules) and record whether the obligation ledgers are reviewable, the oracles independent, and coverage reported without a defect-absence claim. Done 2026-10-27 (`evals/results/q04-claude-code-2026-10-27.json`): 4 of 4 planted defects found in each run; Q04-G01-F01 (examples carried no obligations, so two sessions wrote none) is fixed and the rerun recorded ledgers on both.
  - [ ] Q04-G02: Decide whether a static read counts as exercising an obligation (Q04-G01-O01: a read-only attempt with a `fail` outcome counted as exercised), and encode the answer in the pack or `obligation_coverage`.
  - [ ] Q04-G03: Repeat the lane on more than one run per fixture and on a real repository's specification before treating the ledger rate as stable.

### Q05 - Add non-functional session packs

- **Status:** Done (2026-10-29). The four packs are pinned by `tests/test_nfr_packs.py`, and on the installed plugin both boundary requests stopped `inconclusive` before acting (Q05-G01)
- **Importance:** High
- **Complexity:** Hard
- **Depends on:** Q02, authorization policy evaluation
- **Approach:** Add separate packs for performance, resilience/recovery, accessibility/compatibility/i18n, and data integrity; keep security integration separate.
- **Done when:** Every pack states workload/threat/population, environment, oracle, uncertainty, stop conditions, and evidence; risky effects fail closed.
- **Follow-ups:**
  - [x] Q05-G01: Run one non-functional request per pack through the installed plugin, including one that would need load, fault injection or real data, and record whether the agent reads the pack, stays local, and stops as `inconclusive` at the authority boundary instead of acting. Done 2026-10-29: 4 of 4 packs read after Q05-G01-F01's routing fix; `evals/results/q05-claude-code-2026-10-29.json`.
  - [ ] Q05-G02: Repeat the lane on more than one run per case and on a real service before treating the boundary behavior as stable.

### Q06 - Evaluate backlog-kit interoperability

- **Status:** In progress. The offline interoperability check runs against a real backlog kit (2026-10-27); all seven checks hold since the backlog kit refuses a repeated handoff (Q06-F02)
- **Importance:** High
- **Complexity:** Medium
- **Depends on:** Stable Agentic Backlog Kit ingestion contract
- **Approach:** Export confirmed findings, validate them with the sibling kit, ingest only after explicit request, and prove QA evidence remains linked without duplicating backlog state.
- **Done when:** Confirmed findings become valid Bug items, candidates are rejected, missing business inputs are never guessed, and synchronization remains outside this plugin.
- **Follow-ups:**
  - [x] Q06-F01: The handoff example used status `Backlog`, which the backlog kit's default workflow does not define, so following it failed ingestion. The example now uses `Inbox`, and the contract says the status comes from the backlog manifest's `workflow.statuses` (2026-10-27).
  - [x] Q06-F02: Ingesting the same confirmed finding twice created a second Bug. Felix chose a backlog-kit guard (2026-10-27): items accept a unique `source`, the export sets it to the session and finding, and a repeat is refused.
  - [ ] Q06-O01: `abk init` over an existing manifest exits with a Python traceback rather than a JSON error. This is a backlog-kit report, not a QA kit defect.

### Q07 - Decide whether to build an MCP server

- **Status:** Done (2026-10-29). Keep the skills-only architecture: [docs/q07-mcp-decision.md](docs/q07-mcp-decision.md) records the transcript measurements, the reading of each gap, and when to revisit
- **Importance:** Conditional
- **Complexity:** Hard
- **Depends on:** Q01, Q02, token/call measurements
- **Approach:** Measure whether host tools plus the local ledger leave authorization, compact-query, portability, or structured-result gaps.
- **Done when:** Evidence supports either retaining the skills-only architecture or building a narrowly scoped server with explicit tools and permissions.
- **Follow-ups:**
  - [ ] Q07-G01: After the CLI fixes in the decision record, repeat `scripts/q07_measure.py` on the next lane's transcripts. Revisit the decision if payload discovery stays above about 20% of tool calls; that also answers Q02-O01.

### Q08 - Agentic-system assurance pack

- **Status:** Done for its done-when (2026-11-05); M6 items remain open. In two sessions against a seeded toy support agent, each ran 10 seeds in a sandbox reset before every trial, judged all six dimensions separately, and reported utility at 1.0 while confidentiality failed as a critical breach on both leaking seeds (Q08-G01).
- **Importance:** Later
- **Complexity:** Hard
- **Depends on:** M4/M5 contracts, Q07 decision
- **Approach:** Test complete trajectories, side effects, policy decisions, memory, multi-agent handoffs, recovery, consistency, and budgets in resettable environments. Slice 1: an attempt may carry `trial` (index, seed, a verdict per dimension, `critical` only on a fail). `qa.py trials` reports per charter and dimension, with pass rates over judged trials, inconclusive excluded, rates withheld below 5, critical breaches listed by trial and no composite score. A dimension with any critical breach is `critical-breach` whatever its rate. The qa-session `agentic-systems` pack covers the trial plan, the reset, oracles per dimension, the LLM-judge limit and fail-closed authority for hosted models and real tools.
- **Done when:** Utility, safety, authorization, confidentiality, recovery, and cost are independently measured and critical invariant breaches cannot be averaged away.
- **Follow-ups:**
  - [x] Q08-G01: A seeded support agent that leaks a card number to an external address on one seed in five and overruns its tool budget on another, through the installed plugin. 2 of 2 sessions flagged every leaking seed critical and every overrun as a cost fail, with no false flag and no hosted-model call; `evals/results/q08-claude-code-2026-11-05.json`. The lane's seed detection missed harness scripts and now also reads seeds from the ledger (Q08-G01-O01).
  - [x] Q08-G02: Run 1 measured no recovery, reading the fixture's own fault switch as fault injection that needs approval (Q08-G01-O02). After the pack named it a local check, run 2 judged recovery in 2 of 2 sessions, with every other verdict still correct (Q08-G01-O04).
  - [x] Q08-G03: A `control` dimension, an operator stop and a ticket that must go to a person. Without being asked, 2 of 2 sessions stopped the agent mid-ticket and handed the over-limit ticket off. A replay of all 55 trials showed every leak, overrun and ignored stop flagged and nothing flagged on a clean trial; `evals/results/q08-g03-claude-code-2026-11-05.json`.
  - [ ] Q08-G04: Trajectory and memory oracles, multi-agent handoff, hidden scenario families, and rollback of partial side effects (the rest of M6). Rollback, state and trajectory oracles done (2026-11-05): with a credit-note ledger outage and a stop between a refund and its credit note, 2 of 2 sessions ran both without being asked, flagged every refund left without a credit note as a critical recovery fail, and flagged nothing on a clean trial; `evals/results/q08-g04-claude-code-2026-11-05.json`. Memory, multi-agent handoff and hidden scenario families remain.

### Q09 - Dogfood the kit on itself under Claude Code

- **Status:** Complete for its done-when; follow-up items remain open
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
  - [x] Run `qa-discover` against this repository through the installed plugin and retain the profile and charters (Q01-DISC-DIRECT and both self-QA sessions, 2026-10-16).
  - [x] Execute at least one bounded session with real attempts and record them with `attempt-add`: `qa-self-20261015-wf` (15 attempts) and `qa-q09-rc-010` (17 attempts) on the release candidate.
  - [x] Produce an evidence package and a disposition, and record the limitations the session could not close: [Q09 self-QA report](docs/q09-self-qa-2026-10-16.md) (hold on both, scoped to what was tested).
  - [x] Feed anything confirmed back into this roadmap as tracked work (Q09-F01 to Q09-F07 below).
  - [x] Q09-F01: Concurrent writers to one session silently lost records; 16 parallel `attempt-add` calls all exited 0 and left 1 record. Every session write now holds an OS file lock, with a 12-writer regression test (2026-10-16).
  - [x] Q09-F02: `finding-update` could rewrite a confirmed finding's `actual`, `expected` and `recorded_at` and erase a candidate's evidence. History fields are now append-only and observation fields are fixed once a finding leaves `candidate` (2026-10-16).
  - [x] Q09-F03: Five of the new finding-history rules had no test that fails when their guard is removed (found by `qa-q09-rc-010`). Every settled and append-only field now has one, and each guard removal fails the suite (2026-10-16).
  - [x] Q09-F04: A confirmed finding's reproduction, severity and acceptance criteria could still change without trace. Owner decision (2026-10-22): lock them. Once a finding leaves `candidate`, the ledger rejects changes to its severity, acceptance criteria and reproduction preconditions, steps and reproducibility; `reproduction.attempts` still counts newly linked attempts.
  - [x] Q09-F05: `.agentic-qa/manifest.json` `defaults.evidence_root` was validated but never used. Owner decision (2026-10-22): honor it. The ledger stores sessions under it and refuses a root that resolves outside the repository.
  - [x] Q09-F06: `CLAUDE.md` under-stated the plugin manifest's accepted validator warnings (2026-10-16).
  - [x] Q09-F07: The roadmap's date and its links to uncommitted Q01 results had gone stale (2026-10-16).
  - [ ] Q09-G01: Probe concurrent writes on Windows and macOS, and interrupted writes with authorization; the 2026-10-16 sessions covered Linux and Python 3.13 only.

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

### Q11 - Add the suite-trust session pack

- **Status:** Done (2026-10-29). The pack is pinned by `tests/test_nfr_packs.py`; on the installed plugin both sessions found both planted causes, classified them correctly, and changed nothing (Q11-G01)
- **Importance:** High
- **Complexity:** Medium
- **Depends on:** Q05
- **Approach:** M5's first item. A `qa-session` reference for flaky, order-dependent and retried suites that varies one entropy source at a time, separates product defects from test defects, and never edits a suite to make it pass.
- **Done when:** A session asked whether a suite can be trusted finds the entropy a verdict depends on, classifies each cause, says what a retry policy hides, and edits no test, CI file or dependency.
- **Follow-ups:**
  - [x] Q11-G01: Run the request through the installed plugin on a fixture with a hash-seed product defect, an order-dependent test and CI retries. Two of two sessions read the pack and found both causes; `evals/results/q11-claude-code-2026-10-29.json`.
  - [ ] Q11-G02: Add fixtures for time-zone, locale, wall-clock and leftover-file dependence, and a real repository's flaky suite, before treating the classification rate as stable.

### Q12 - Learn from escapes and incidents in discovery

- **Status:** Done (2026-10-29). On the installed plugin, after two routing fixes, both sessions entered discovery, read the escapes reference, planned without running anything, cited the postmortem in every charter, and kept the customer's data out of the ledger (Q12-G01)
- **Importance:** High
- **Complexity:** Medium
- **Depends on:** Q11
- **Approach:** M5's fourth item. A `qa-discover` reference that turns supplied incident material and confirmed findings into a raised risk and a regression charter. It treats an escape as evidence about the checks, never as new intent.
- **Done when:** A QA round planned after an incident names the check that missed it, adds a regression charter whose oracle is the observed failure and that cites the incident, copies no personal data into the ledger, and runs nothing it was not asked to run.
- **Follow-ups:**
  - [x] Q12-G01: Plan from a postmortem through the installed plugin. Run 1 never reached discovery (Q12-G01-F01, fixed in `qa-workflow` and the `qa-discover` description), and the lane's own suffix asked for execution (Q12-G01-F02, fixed); run 3 met the done-when in 2 of 2 sessions; `evals/results/q12-claude-code-2026-10-29.json`.
  - [ ] Q12-G02: Repeat with an escape recorded as a confirmed finding in an existing ledger, not only as a postmortem, and with incident material that contradicts the documented behavior.

### Q13 - Verify observability contracts and diagnosability

- **Status:** Done (2026-11-01). On the installed plugin, both sessions read the observability pack, triggered every documented failure path through local fakes, judged each from the signals alone, found both contract breaks, kept the card number out of the ledger and left the production log store alone (Q13-G01)
- **Importance:** High
- **Complexity:** Medium
- **Depends on:** Q11
- **Approach:** M5's second item. A `qa-session` reference for the `observability` quality attribute: name the signal contract, trigger one known failure at a time, and answer which request failed, where and why from logs and metrics alone before reading code. Production or shared telemetry needs its own approval.
- **Done when:** A session asked whether a system can be diagnosed from its signals triggers each documented failure path locally, checks every path against the written contract, names the paths it could not diagnose or did not trigger, copies leaked secrets into the ledger only masked, and queries no production telemetry without approval.
- **Follow-ups:**
  - [x] Q13-G01: Run against a service with a written contract through the installed plugin. 2 of 2 sessions met the done-when; the lane's first production-store detector gave a false failure (Q13-G01-O01, fixed and re-judged); `evals/results/q13-claude-code-2026-11-01.json`.
  - [ ] Q13-G02: Repeat on a system with no written contract and on one whose signals go to a local collector (traces, structured metrics), so diagnosability is judged without a contract table.

### Q14 - Production session modes under recorded approval

- **Status:** Done (2026-11-02). Against a local rollout simulator, the session with no approval and the one with an expired approval touched nothing in production and closed blocked; the one with a valid approval recorded it, stayed in scope, and stopped at the abort trigger without promoting or rolling back (Q14-G01)
- **Importance:** High
- **Complexity:** Medium
- **Depends on:** Q13
- **Approach:** M5's third item. The owner decided on 2026-11-02 that production work needs a recorded, expiring approval and is evaluated only against local simulations. The ledger adds the `progressive-delivery`, `synthetic`, `shadow` and `field-feedback` modes. Each one requires `production_authorization` (approver, approval and expiry times, environment, scope, blast radius, abort trigger, rollback). `session-create` refuses an expired approval, and after expiry `attempt-add` takes only `inconclusive`. `qa-session`'s session-design reference says never to invent or widen an approval, to act only within scope, and to stop at the abort trigger.
- **Done when:** A session asked to check something in production starts only from an approval given for that work, records it unchanged, refuses an expired one, sends nothing to production outside its approved environment, never promotes or rolls back unless the scope names it, and stops at the abort trigger.
- **Follow-ups:**
  - [x] Q14-G01: Three cases (no approval, expired, valid in the simulator) through the installed plugin, met in 3 of 3; `evals/results/q14-claude-code-2026-11-02.json`.
  - [ ] Q14-G02: Cover the `shadow` and `field-feedback` modes, an abort trigger that fires mid-run, an approval that expires during the session, and field data that carries personal data.

### Q15 - Cross-session metrics without individual ranking

- **Status:** Done (2026-11-02). Over a seeded ledger of eight closed sessions, all four sessions ran `metrics`, quoted rates with numerators, denominators and intervals, called out withheld groups, changed nothing, and declined to rank testers although a rota mapped sessions to names (Q15-G01). M5 is complete.
- **Importance:** High
- **Complexity:** Medium
- **Depends on:** Q14
- **Approach:** M5's last item. `qa.py metrics` reads closed sessions and reports outcome and finding counts, obligation coverage, and three rates: inconclusive or error attempts, confirmed among resolved findings, and obligations exercised. Each rate has a 95% Wilson interval. A rate on fewer than 5 is withheld. Sessions that are open or have a broken chain are excluded and counted. Groups are by quality attribute, mode or risk tier only. There is no person or agent view, and the guardrails travel with the output. `qa-report` routes trend questions to it and refuses to rank people, even when asked.
- **Done when:** A trend report across sessions quotes each rate with numerator, denominator and interval, withholds small samples, changes nothing in the ledger, and declines to rank or compare people even when asked and when another file maps sessions to names.
- **Follow-ups:**
  - [x] Q15-G01: Seeded ledger plus a request to name the top tester, through the installed plugin. Run 1's lane judged the seeded sessions (Q15-G01-O01, fixed); run 2 met the done-when in 2 of 2; `evals/results/q15-claude-code-2026-11-02.json`.
  - [ ] Q15-G02: Add escapes per release and time-to-confirm once the ledger records release identity and escape links, and repeat on a ledger large enough that no group is withheld.

### Q16 - Add Antigravity as a supported host

- **Status:** Not started. Added 2026-11-11: the owner confirmed the missing manifest is a gap against the organization's three-host rule.
- **Importance:** Medium
- **Complexity:** Easy
- **Depends on:** Nothing
- **Approach:** Add `.antigravity-plugin/plugin.json` over the same `skills/`, using only fields its schema lists, as `agentic-backlog-kit` and `agentic-product-playbook` do. Extend `tests/test_host_manifest_parity.py` to cover it, and state in the README which hosts are validated.
- **Done when:** `agy plugin validate .` passes, the parity test covers three manifests, no skill content is forked, and the README and `CLAUDE.md` name the validated hosts.

### Q17 - Supply evidence across Seam B

- **Status:** Not started; blocked on the contract. Added 2026-11-11.
- **Importance:** High
- **Complexity:** Medium
- **Depends on:** `aio-agentic-sdlc` ROADMAP M5 defining the Seam B contract and fixture
- **Approach:** Export a confirmed finding in the versioned form the framework reads, with a fixture held byte-identical in both repositories as for Seam A. The framework chooses and records the disposition; this kit adds no disposition of its own. Q09's done-when had the kit disposition its own defects, which was written before that decision.
- **Done when:** The framework can read a confirmed finding from this kit's export, map it to an Intention node or report it unmapped, and the standalone Bug handoff is unchanged.

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
