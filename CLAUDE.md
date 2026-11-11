# Agentic QA Kit — Claude Code guidance

@AGENTS.md

The instructions above are the canonical repository guidance and apply in full.
This file adds only what differs when the host is Claude Code.

## Organization authority model

`aio-agentic-sdlc` is the organization's end product: a framework whose backlog
is the diff between intended and actual software. This kit closes its loop with
QA evidence and is also used on its own. The normative statement of which
repository owns which kind of truth is `doc/authority-model.md` in
`aegolius-labs/aio-agentic-sdlc`.

In the composed system this kit owns **layer 5**: evidence about reality. It does
not decide disposition and does not manage a backlog. The framework chooses a
finding's disposition when it consumes the finding, and records the choice and
the reason (owner decision, 2026-11-11). A finding has exactly two legitimate
dispositions:

- `revert-node` — the defect falls inside existing accepted intent, so the
  responsible Intention DAG node is reverted to an open state and the work
  regenerates from the diff. No new work item is created. This is the default
  inside a full `aio-agentic-sdlc` pipeline.
- `bug-handoff` — the defect falls outside modeled intent, or this kit is being
  used standalone. Emit one Bug payload for Agentic Backlog Kit ingestion.

This kit supplies the evidence for that choice: the confirmed finding, its
reproduction and its limitations. The ledger has no disposition field for it,
and the contract between the two repositories (Seam B) is not built yet.
Emitting a Bug payload for a defect that belongs to an existing accepted node
creates a second competing record of the same work and is a contract violation,
so inside a full pipeline do not hand off a Bug before the framework has chosen.

Used standalone, `bug-handoff` is the only disposition available. That is a
supported configuration, not a degraded mode.

## Host manifests

The plugin ships one manifest per host, and they must agree:

- `.codex-plugin/plugin.json` — Codex
- `.claude-plugin/plugin.json` — Claude Code
- `.claude-plugin/marketplace.json` — Claude Code marketplace entry
- `.antigravity-plugin/plugin.json` — Antigravity

The Antigravity manifest declares no version and no `skills` key, like the
Claude Code ones. Antigravity's schema is closed but `agy plugin validate`
accepts unknown keys silently, so the parity test pins the schema's key list.
As of Q16 the manifest exists but `agy plugin validate .` has not been run
(no `agy` CLI where it was added), so Antigravity is not yet a validated host.

`skills/` is the single source of truth for behavior and is auto-discovered by
all three hosts. Do not fork skill content per host.
`tests/test_host_manifest_parity.py` enforces that `name` and `description`
agree across manifests, that only the Codex manifest declares a version, and
that every host discovers the same skills, and that the Antigravity manifest
stays within its published schema keys. The Codex manifest currently carries
an evaluation-provenance suffix after `+`, which is deliberate and referenced by
Q01.

Validate Claude Code manifests with the bundled validator:

```powershell
claude plugin validate .claude-plugin/plugin.json
claude plugin validate .claude-plugin/marketplace.json
claude plugin validate skills --strict
```

The two manifests are validated without `--strict` because they emit known,
accepted warnings. The plugin manifest emits two:

> `root: CLAUDE.md at the plugin root is not loaded as project context.`

That is correct and expected. `CLAUDE.md` here is guidance for contributors
working *in* this repository, not context shipped to plugin consumers. Everything
a consumer needs lives in `skills/`. Do not silence the warning by moving
repository guidance into a skill.

It also emits `version: No version specified`, and the marketplace manifest
emits the same as `plugins[0] plugin.json → version: No version specified`. That is deliberate (decided 2026-10-06, following
agentic-backlog-kit). The Claude Code manifests declare no version, so Claude
Code versions the plugin by commit and `claude plugin update` delivers new
skills. A declared version that never moves would make Claude Code keep the
first installed copy forever. `tests/test_host_manifest_parity.py` fails if a
version is added back. Any other warning from either manifest is a failure, and
`skills/` must keep passing `--strict`.

Since Claude Code 2.1.307 the plugin manifest validation also runs a subset of
the plugin directory's checks, which do not change the result. It reports
`ICON_MISSING` and notes that this folder also holds a marketplace manifest.
Both are accepted: the kit is not submitted to the plugin directory, the note
is informational, and a listing icon can be set only once, at first
submission, so choosing one is the owner's decision. CI pins Claude Code
2.1.307.

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
