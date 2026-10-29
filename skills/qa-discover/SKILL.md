---
name: qa-discover
description: Discover an unfamiliar codebase and turn product context, repository structure, runtimes, existing checks, risks, and evidence gaps into a QA profile and bounded charters. Use before broad QA planning or when the runnable/test surface is unclear; do not use merely to execute an already specified check.
---

# Discover a QA target

Discovery is read-only unless the user also requested persistent QA artifacts.

1. Read all applicable repository instructions. Capture the repository/worktree identity, current revision when available, dirty state, and any generated or vendored boundaries.
2. Inspect high-signal files before broad traversal: project manifests, lockfiles, entry points, build/test configuration, CI workflows, container/IaC files, public contracts, migrations, observability configuration, and existing test directories.
3. Identify intended use, primary users, critical journeys, system boundary, external dependencies, data sensitivity, supported environments, and known obligations from repository evidence. Mark unknowns instead of inventing them.
4. Map the runnable surface: languages/toolchains, standard commands, test layers, fixtures, environments, services, UI/browser needs, network needs, and missing dependencies. Prefer repository-declared commands over guessed conventions.
5. Select relevant quality attributes and translate each into a scoped assurance question. Rank risks by consequence, uncertainty, exposure, detectability, reversibility, and evidence value; do not collapse hard security/safety constraints into an average score.
6. Review existing evidence for relevance, oracle validity, provenance, freshness, reproducibility, and claim coverage. A test count or coverage percentage is not a confidence claim by itself.
7. Produce a small charter set ordered by information value and risk. Each charter needs a risk, quality attribute, method, independent oracle, scope, budget, stop conditions, and required authorization.
8. When persistence is requested, initialize the ledger if needed and create a discovery or full session from the reviewed input. Do not install dependencies or execute checks in this skill unless the user also asked to proceed into a session.

Read [references/discovery-contract.md](references/discovery-contract.md) for the output shape and technique-routing questions. When a defect reached users or an incident is supplied, also read [references/escapes.md](references/escapes.md).
