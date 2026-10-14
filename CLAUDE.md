# Agentic QA Kit — Claude Code guidance

@AGENTS.md

The instructions above are the canonical repository guidance and apply in full.
This file adds only what differs when the host is Claude Code.

## Organization authority model

This repository is one of three related Aegolius Labs repositories. The
normative statement of which repository owns which kind of truth is
`doc/authority-model.md` in `aegolius-labs/aio-agentic-sdlc`.

In the composed system this kit owns **layer 5**: evidence about reality. It does
not decide disposition on its own and does not manage a backlog. A finding has
exactly two legitimate dispositions:

- `revert-node` — the defect falls inside existing accepted intent, so the
  responsible Intention DAG node is reverted to an open state and the work
  regenerates from the diff. No new work item is created. This is the default
  inside a full `aio-agentic-sdlc` pipeline.
- `bug-handoff` — the defect falls outside modeled intent, or this kit is being
  used standalone. Emit one Bug payload for Agentic Backlog Kit ingestion.

Record which disposition was chosen and why. Emitting a Bug payload for a defect
that belongs to an existing accepted node creates a second competing record of
the same work and is a contract violation.

Used standalone, `bug-handoff` is the only disposition available. That is a
supported configuration, not a degraded mode.

## Host manifests

The plugin ships one manifest per host, and they must agree:

- `.codex-plugin/plugin.json` — Codex
- `.claude-plugin/plugin.json` — Claude Code
- `.claude-plugin/marketplace.json` — Claude Code marketplace entry

`skills/` is the single source of truth for behavior and is auto-discovered by
both hosts. Do not fork skill content per host.
`tests/test_host_manifest_parity.py` enforces that `name` and `description`
agree across manifests, that only the Codex manifest declares a version, and
that both hosts discover the same skills. The Codex manifest currently carries
an evaluation-provenance suffix after `+`, which is deliberate and referenced by
Q01.

Validate Claude Code manifests with the bundled validator:

```powershell
claude plugin validate .claude-plugin/plugin.json
claude plugin validate .claude-plugin/marketplace.json
claude plugin validate skills --strict
```

The two manifests are validated without `--strict` because each emits one
known, accepted warning. The plugin manifest emits:

> `root: CLAUDE.md at the plugin root is not loaded as project context.`

That is correct and expected. `CLAUDE.md` here is guidance for contributors
working *in* this repository, not context shipped to plugin consumers. Everything
a consumer needs lives in `skills/`. Do not silence the warning by moving
repository guidance into a skill.

The marketplace manifest emits `plugins[0] plugin.json → version: No version
specified`. That is deliberate (decided 2026-10-06, following
agentic-backlog-kit). The Claude Code manifests declare no version, so Claude
Code versions the plugin by commit and `claude plugin update` delivers new
skills. A declared version that never moves would make Claude Code keep the
first installed copy forever. `tests/test_host_manifest_parity.py` fails if a
version is added back. Any other warning from either manifest is a failure, and
`skills/` must keep passing `--strict`.

`python scripts/validate_plugin.py` runs all three validations and enforces
exactly this: CI runs it on every pull request. If an accepted warning changes,
update its allowlist and this section together.

## Installing locally

```powershell
claude plugin marketplace add ./agentic-qa-kit
claude plugin install agentic-qa-kit@aegolius-labs-qa
```

## Skill invocation

Skill bodies use Codex's `$skill-name` reference syntax when one skill points at
another. In Claude Code the equivalent is model invocation by description, or
`/agentic-qa-kit:skill-name` typed explicitly. Read a `$name` reference as "use
that skill", not as a literal command to type.

## Authorization

This kit's invariants bind regardless of host. In Claude Code specifically, a
permission-mode allowance, a previously approved Bash pattern, or a tool granted
in an earlier turn is **not** point-of-action authority. Destructive tests,
production access, dependency installation, external messages, and material cost
each require explicit authorization at the moment of the action, even inside a
workflow the user already asked for.

## Verification

```powershell
python -c "import sys, unittest; sys.path.insert(0, 'src'); suite=unittest.defaultTestLoader.discover('tests'); result=unittest.TextTestRunner(verbosity=2).run(suite); raise SystemExit(not result.wasSuccessful())"
python scripts/qa.py --help
```

The Bash tool is also available on Windows here. The same suite runs with:

```bash
PYTHONPATH=src python -m unittest discover -s tests
```
