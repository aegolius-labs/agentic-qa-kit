# Releases

Agentic QA Kit releases through the Aegolius Labs organization workflow, the
same one Agentic Backlog Kit uses. Nothing is published by hand and nothing goes
to PyPI. A release is a GitHub Release carrying a wheel and an sdist.

## What cuts a release

Pull requests merge by squash, and the PR title becomes the single Conventional
Commit the version calculator reads.

| Commit type | Effect |
| --- | --- |
| `feat:` | minor version |
| `fix:`, `perf:` | patch version |
| `feat!:` or a `BREAKING CHANGE:` footer | major version |
| `docs:`, `test:`, `ci:`, `chore:`, `refactor:`, `style:`, `build:` | no release |

Pick the type for what a consumer of the plugin would notice. A merge that
changes only evaluation evidence is `test:` even when it took real work.

Under the organization's release-automation exception, a release-bearing
commit merged to `main` is the authorization for its tag, GitHub Release and
asset upload. No separate confirmation follows.

## The pipeline

`.github/workflows/release.yml` runs on every push to `main` and can be started
by hand with `workflow_dispatch`.

1. **compute-version** derives the next version from the commits since the last
   `v*` tag, without writing anything.
2. **baseline-guard** runs when no version was computed. It fails if there is no
   `v*` tag at all, because then "no release" would mean "no history", not
   "nothing release-bearing". It never creates a tag.
3. **preflight** checks out the exact candidate commit, then:
   - runs the unit suite, `qa.py --help` and `budgets.py --check`;
   - stamps the computed version with `scripts/set_version.py`;
   - builds the distributions and checks them with `scripts/release_check.py`;
   - installs the wheel and runs `aqk --help`;
   - binds the files, hashes, tag and commit with `scripts/release_inventory.py`.
4. **release** hands that exact bundle to the organization publisher. It creates
   the tag and a draft release, uploads and verifies the assets, publishes, and
   checks that the release is immutable.

### Versions are stamped, not predicted

Nothing in the tree has to declare the next version. `set_version.py` writes the
computed version into `pyproject.toml`, `.codex-plugin/plugin.json` and
`src/agentic_qa_kit/__init__.py`, and turns `## [Unreleased]` in
`CHANGELOG.md` into that version's entry. It runs only inside preflight and
commits nothing; the tag records what a version means.

Because nothing is committed back, the first change after a release promotes
the released section in the committed `CHANGELOG.md` with that release's date,
so `## [Unreleased]` holds only unreleased work.

The Claude Code manifests declare no version, on purpose. Claude Code installs
from the repository rather than the release assets and versions an undeclared
plugin by commit, so `claude plugin update` keeps delivering new skills.

### The baseline

The history starts at the lightweight tag `v0.0.0` on `c0b1ccf`, the last
commit before release automation (owner decision, 2026-10-16). The first
`feat:` merge after it computes `v0.1.0`.

## Repository settings

- Immutable releases are enabled and enforced by the organization owner.
- The repository is private on the free plan, so rulesets and branch protection
  are not available. Merging only green pull requests is a working rule, not an
  enforced one.

## Recovery

The preflight bundle is kept for 30 days. If publication fails, re-run only the
failed `release` job: a matching draft resumes, and an identical published
release is a verified no-op. Never delete assets or move a tag. Changed assets
or identities stop for a reviewed fix. After the bundle expires, a rebuild is
not proof of byte identity.
