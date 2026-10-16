# Contributing

Issue reports, design discussion, and documentation feedback are welcome.

This project uses a noncommercial plus paid-commercial dual-licensing model.
Aegolius Labs must have sufficient rights to distribute every code contribution
under both models. Until a contributor agreement process is published, external
code pull requests cannot be accepted or merged. This avoids accepting code
under terms that would make commercial licensing ambiguous.

Do not submit code copied from another project unless its license is compatible
and the source and license are clearly identified. Never submit secrets,
production data, or private QA evidence.

Changes should preserve the invariants in [AGENTS.md](AGENTS.md), include tests
proportional to risk, and pass the complete local suite, the plugin validation,
and the byte budgets:

```bash
PYTHONPATH=src python -m unittest discover -s tests
python scripts/validate_plugin.py
python scripts/budgets.py --check
```

`skills/` is the single source of truth for both hosts. Do not fork skill
content per host.

Commits intended for `main` use Conventional Commits, and the squash-merge
title is the commit that counts. `fix:` selects a patch release, `feat:` selects
a minor release, and a `BREAKING CHANGE:` footer or breaking `!` selects a major
release. Other types (`docs:`, `test:`, `ci:`, `chore:`, `refactor:`) do not
release. Write user-visible changes under `## [Unreleased]` in
[CHANGELOG.md](CHANGELOG.md). The release workflow computes the version from
commit history, stamps it into `pyproject.toml`, the runtime, the Codex
manifest, and the changelog heading of the built artifacts, and publishes; see
[docs/release.md](docs/release.md).
