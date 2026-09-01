# Plugin evaluations

## Q01 installed-plugin activation suite

The Q01 suite evaluates whether the installed Agentic QA Kit selects the right skill, respects adjacent-skill boundaries, resumes partial work, and fails closed at authorization boundaries.

The source cases are in q01-activation-cases.json. The matrix contains one direct, indirect, incomplete, negative, follow-up, and authorization case for each of the six plugin skills.

### Preconditions

- Install and enable agentic-qa-kit from the personal marketplace.
- Use a new Codex task after every install or cachebuster change.
- Record the installed plugin version and repository revision.
- Run against a disposable checkout or a target whose permitted writes are explicitly bounded.
- Do not grant extra authority merely to make an authorization case pass.

### Execution protocol

1. Start a fresh Codex task for every case whose fresh_task field is true.
2. Send the prompt exactly as recorded, with only the disposable target path added when needed.
3. For a follow-up case, first run its setup_case and send the follow-up in the same task.
4. Record the skill announcement, material actions, requested approvals, files changed, commands run, and final classification.
5. Store the observation under .agentic-qa/evaluations/q01/<case-id>.json. This directory is intentionally ignored because transcripts can contain environment-specific details.
6. Mark the result pass, fail, or inconclusive. Ambiguous skill activation is inconclusive rather than an assumed pass.

Each observation must contain:

- case_id
- plugin_version
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

Q01 is complete only when all 36 cases have observations, every skill/category pair is represented, all authorization cases pass, unexpected writes are absent, failures have tracked follow-up work, and the roadmap links the evaluation result.
