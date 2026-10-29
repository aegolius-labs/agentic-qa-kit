# Agentic QA Kit

Agentic QA Kit is a plugin for evidence-centered software quality assurance, supported on Claude Code and Codex. It equips agents to discover unfamiliar codebases, design risk-based QA work, run bounded sessions, identify and reproduce defects, preserve auditable evidence, and hand confirmed work to a backlog system.

The design is derived from `Modern_Quality_Engineering_2026.md`: quality is a contextual claim supported by versioned evidence, not a test count or a green dashboard.

## Included workflows

- `qa-workflow`: orchestrate a full lifecycle or resume at a requested stage.
- `qa-discover`: map the product context, codebase, execution surface, risks, quality attributes, and evidence gaps.
- `qa-session`: plan and execute bounded functional, exploratory, regression, static, integration, or non-functional charters.
- `qa-reproduce`: control, repeat, minimize, and classify a suspected anomaly.
- `qa-report`: normalize attempts and findings into an evidence package and QA session report.
- `qa-backlog-handoff`: generate a reviewed Bug payload and optionally feed it to Agentic Backlog Kit.

The skills use the host's existing repository, shell, browser, and connector capabilities. There is deliberately no MCP server ([Q07 decision](docs/q07-mcp-decision.md)): the local ledger supplies deterministic artifact handling while the agent selects the tools already available in the host.

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

## Installing

`skills/` is the single source of truth for behavior on every host and is
auto-discovered. Each host reads its own thin manifest: `.claude-plugin/` for
Claude Code, `.codex-plugin/plugin.json` for Codex. Skill content is never forked
per host.

Claude Code, from a checkout of this repository's parent directory:

```powershell
claude plugin marketplace add ./agentic-qa-kit
claude plugin install agentic-qa-kit@aegolius-labs-qa
```

The same user-scoped install serves both the Claude Code CLI and the desktop app.

A marketplace added from GitHub (`claude plugin marketplace add
aegolius-labs/agentic-qa-kit`) installs a cached copy. To take new skills,
refresh the marketplace, update, and restart Claude Code:

```bash
claude plugin marketplace update aegolius-labs-qa
claude plugin update agentic-qa-kit@aegolius-labs-qa
```

Claude Code shows the plugin's version as a short commit id, not a release
number: the Claude Code manifests declare no version on purpose, so that each
commit counts as a new version. A GitHub install made before 2026-10-06 is stuck
at `0.1.0` and says it is already up to date; uninstall and install it once.

For Codex, add this plugin to a local or repository marketplace and install it
from the Plugins Directory.

## Limitations

What 0.1.0 does not establish, so nobody has to infer it:

- **Activation evidence is narrow.** The Q01 Claude Code lane ran every case
  once, on the headless CLI, against the skills as written at a commit. It shows
  that each case can pass. It does not show how often a case passes, how the
  desktop app behaves, or how this published artifact behaves. See
  [the lane result](evals/README.md#claude-code-lane-results).
- **Codex is supported but less evidenced.** The Codex lane's observations are
  inconclusive on provenance (roadmap item Q10).
- **The ledger trusts the agent.** It validates structure and history rules, but
  it does not run tests or check that evidence files say what an attempt
  claims. Evidence digests are optional.
- **Locking is local.** Writers are serialized with an operating-system file
  lock, which network filesystems may not honor.
- **No backlog of its own.** Handoff produces one Agentic Backlog Kit `Bug`
  payload. Ingestion and GitHub synchronization happen in that kit, under its
  plan and confirmation rules.
- **Known open findings** are tracked in [ROADMAP.md](ROADMAP.md), including
  the Q09 self-QA results.

## License

Agentic QA Kit is source-available under the
[PolyForm Noncommercial License 1.0.0](LICENSE.md). Commercial use needs a
separate license; see [COMMERCIAL.md](COMMERCIAL.md).

## Plugin development

For installed testing, install through a local marketplace, start a new
top-level task, and exercise direct, indirect, incomplete, negative, and
authorization-sensitive prompts. Note that a Claude Code directory marketplace
installs in place, so the install resolves to the working tree; see
`evals/README.md` for what that does and does not evidence.

Development checks:

```powershell
python -c "import sys, unittest; sys.path.insert(0, 'src'); suite=unittest.defaultTestLoader.discover('tests'); result=unittest.TextTestRunner(verbosity=2).run(suite); raise SystemExit(not result.wasSuccessful())"
python scripts/qa.py --help
```

See `ROADMAP.md` for the current checkpoint, dependencies, and acceptance gates.
