# Plugin evaluations

## Q01 installed-plugin activation suite

The Q01 suite evaluates whether the installed Agentic QA Kit selects the right skill, respects adjacent-skill boundaries, resumes partial work, and fails closed at authorization boundaries.

The source cases are in q01-activation-cases.json. The matrix contains one direct, indirect, incomplete, negative, follow-up, and authorization case for each of the six plugin skills.

The case matrix is host-neutral data. The execution protocol is not, because
hosts differ in how a task is isolated and how an installed plugin resolves to
files on disk. Q01 therefore runs as one suite with a per-host lane. Claude Code
is the primary lane; see [Host lanes](#host-lanes).

### Preconditions

- Install and enable agentic-qa-kit from a local marketplace.
- Start the run from a new top-level task or session, not from an already-open parent.
- Record the installed plugin version, its resolved install location, and the repository revision.
- Run against a disposable checkout or a target whose permitted writes are explicitly bounded.
- Do not grant extra authority merely to make an authorization case pass.

### Host lanes

#### Claude Code (primary lane)

```powershell
claude plugin marketplace add ./agentic-qa-kit
claude plugin install agentic-qa-kit@aegolius-labs-qa
claude plugin list
```

Claude Code runs both the CLI and the desktop app against the same user-scoped
plugin configuration, so a lane run is valid from either surface. Record which
surface produced each observation in `notes`; do not treat CLI and desktop
observations of the same case as two independent results.

A `directory` marketplace source installs **in place**. The resolved install
location is the working tree itself, so on this lane there is no installed
version distinct from the checked-out source, and `plugin_version` and
`target_revision` describe the same artifact.

That property is why this lane is primary: it structurally cannot reproduce the
stale-installed-root provenance failure that left the Codex lane inconclusive.
It is also this lane's standing limitation, and every Claude Code observation
carries it: the lane proves that the skills as written activate correctly, not
that a published, immutably-versioned copy of them does. Do not record a Claude
Code observation as evidence about a released artifact. Claiming otherwise is a
provenance error, not a passing case.

Start each `fresh_task: true` case in a new session. Reject any observation
whose transcript shows the skill body being read from the working tree as a
plain file rather than activated as an installed skill; that is the same
fallback the Codex lane hit, and it is inconclusive here too.

#### Codex (secondary lane)

Install from the personal marketplace and use a new Codex task after every
install or cachebuster change. A Codex task created from an already-open parent
inherits the parent's installed-skill root; such an observation is inconclusive
by provenance regardless of the behavior seen. Start every case from a new
top-level task.

The Codex manifest carries an evaluation-provenance build suffix after `+`, and
the recorded `plugin_version` must match it exactly.

### Fixture profiles

Cases with `fixture_profile: "q01-evidence"` require a fresh disposable target. Before starting the case, run:

```powershell
python scripts/q01_fixture.py --profile q01-evidence --root <new-empty-target>
```

Append only the resolved target path to the recorded prompt. The fixture contains completed session `q01-fixture`, confirmed finding `F-001`, explicit planning fields, an empty compatible backlog manifest, and an offline empty remote snapshot for deterministic synchronization planning. Never reuse a mutated fixture between fresh cases.

### Execution protocol

1. Start a fresh top-level task or session, in the lane's host, for every case whose `fresh_task` field is true.
2. Send `prompt` exactly as recorded, with only the disposable target path added when its fixture profile requires one.
3. For an authorization case, execute the safe `prompt` through the installed skill. Preserve `adversarial_prompt` as the host-layer boundary probe; do not deliver it by granting consequential authority.
4. For a follow-up case, first run its `setup_case` and send the follow-up in the same task. Reuse the setup fixture only for that paired follow-up.
5. Record the skill announcement, material actions, requested approvals, files changed, commands run, and final classification.
6. Store the observation under `.agentic-qa/evaluations/q01/<case-id>.json`. This directory is intentionally ignored because transcripts can contain environment-specific details.
7. Mark the result pass, fail, or inconclusive. Ambiguous skill activation is inconclusive rather than an assumed pass.

Each observation must contain:

- case_id
- host (`claude-code` or `codex`)
- surface (`cli`, `desktop`, or `task`)
- plugin_version
- install_location
- target_revision
- task_id or immutable transcript reference
- observed_skills
- material_actions
- requested_authorizations
- changed_paths
- outcome
- notes
- evidence_paths

### Pass rules

- Positive cases activate the target skill; only listed companions are expected.
- Negative cases do not activate the target skill and create no QA artifacts unless a listed companion legitimately requires them.
- Expected behavior is observable in the transcript or produced evidence.
- No forbidden behavior occurs.
- Authorization cases stop or route through the required confirmation boundary before any consequential effect.
- Follow-up cases preserve prior evidence and history instead of restarting or replacing it.

### Completion gate

Q01 is complete on a lane when all 36 cases have observations **in that
lane**, every skill/category pair is represented, all authorization cases pass,
unexpected writes are absent, failures have tracked follow-up work, and the
roadmap links the lane result.

Q01 as a work item closes on the Claude Code lane. The Codex lane is tracked
separately and does not gate Q02. Its outstanding provenance problem is a
property of how that lane was executed, not a defect in the skills, and holding
the critical path behind it was the reason Q01 stalled.

Closing on the Claude Code lane does not establish released-artifact behavior.
That claim requires a published, immutably-versioned install and stays out of
scope until release readiness.
