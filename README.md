# Agentic QA Kit

Agentic QA Kit is a Codex-first plugin for evidence-centered software quality assurance. It equips agents to discover unfamiliar codebases, design risk-based QA work, run bounded sessions, identify and reproduce defects, preserve auditable evidence, and hand confirmed work to a backlog system.

The design is derived from `Modern_Quality_Engineering_2026.md`: quality is a contextual claim supported by versioned evidence, not a test count or a green dashboard.

## Included workflows

- `qa-workflow`: orchestrate a full lifecycle or resume at a requested stage.
- `qa-discover`: map the product context, codebase, execution surface, risks, quality attributes, and evidence gaps.
- `qa-session`: plan and execute bounded functional, exploratory, regression, static, integration, or non-functional charters.
- `qa-reproduce`: control, repeat, minimize, and classify a suspected anomaly.
- `qa-report`: normalize attempts and findings into an evidence package and QA session report.
- `qa-backlog-handoff`: generate a reviewed Bug payload and optionally feed it to Agentic Backlog Kit.

The skills use Codex's existing repository, shell, browser, and connector capabilities. The first release deliberately has no MCP server: the local ledger supplies deterministic artifact handling while the agent selects the tools already available in the host.

## Local ledger

`scripts/qa.py` manages compact JSON session records without executing tests on its own:

```powershell
python scripts/qa.py init --root PATH_TO_TARGET
python scripts/qa.py session-create --root PATH_TO_TARGET --input session.json
python scripts/qa.py attempt-add SESSION_ID --root PATH_TO_TARGET --input attempt.json
python scripts/qa.py finding-add SESSION_ID --root PATH_TO_TARGET --input finding.json
python scripts/qa.py summary --root PATH_TO_TARGET --session SESSION_ID
python scripts/qa.py backlog-export SESSION_ID FINDING_ID --root PATH_TO_TARGET --input backlog-fields.json
```

Generated target-project state lives under `.agentic-qa/`. A session record binds scope, target revision, charters, attempts, findings, limitations, and decision state. The engine records evidence supplied by the agent; it never turns a tool exit code into a business verdict by itself.

## Backlog boundary

This repository does not manage a backlog. `qa-backlog-handoff` emits one `Bug` item compatible with the Agentic Backlog Kit ingestion contract. It does not prioritize, schedule, synchronize, or mutate GitHub. Those actions remain explicit workflows in `agentic-backlog-kit`.

## Plugin development

The required manifest is `.codex-plugin/plugin.json`, with focused skills under `skills/`. For installed testing, add this plugin to a local or repository marketplace, install it from the Plugins Directory, start a new task, and exercise direct, indirect, incomplete, negative, and authorization-sensitive prompts.

Development checks:

```powershell
python -c "import sys, unittest; sys.path.insert(0, 'src'); suite=unittest.defaultTestLoader.discover('tests'); result=unittest.TextTestRunner(verbosity=2).run(suite); raise SystemExit(not result.wasSuccessful())"
python scripts/qa.py --help
```

See `ROADMAP.md` for the current checkpoint, dependencies, and acceptance gates.
