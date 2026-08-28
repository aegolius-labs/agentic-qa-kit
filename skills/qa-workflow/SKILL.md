---
name: qa-workflow
description: Orchestrate a complete or resumable evidence-centered QA workflow across discovery, session execution, reproduction, reporting, and defect handoff. Use when the user asks for end-to-end QA, autonomous testing, a broad quality assessment, or continuation of a QA effort; use the narrower QA skills for a single named stage.
---

# Orchestrate a QA workflow

Treat quality as a contextual claim supported by bounded evidence. A green check is not defect absence, and automation does not own residual risk.

1. Read repository instructions and establish the exact target, requested outcome, available time/tool budget, and current authorization. Inspect before asking questions that the repository can answer.
2. Locate the plugin root and its `scripts/qa.py`. If the target has no `.agentic-qa/manifest.json`, initialize it only when the requested workflow calls for persistent session evidence; otherwise keep a transient plan and say that evidence was not persisted.
3. Choose the smallest viable path:
   - Full: discovery -> risk/claim profile -> charters -> attempts -> candidate findings -> reproduction -> report -> optional backlog handoff.
   - Partial: enter at the requested stage, load only its prerequisites, and preserve links to any existing session.
   - Resume: run `summary` and targeted `show`; do not reload every raw artifact.
4. Use `$qa-discover` when the context, execution surface, or risk model is unknown. Use `$qa-session` for bounded execution, `$qa-reproduce` for suspected anomalies, `$qa-report` for the evidence package, and `$qa-backlog-handoff` only for confirmed defects.
5. Keep the loop bounded by explicit charters, attempts, time, cost, side effects, and stop conditions. Pause at an action boundary that needs new authority; a request for "full QA" does not authorize dependency installation, destructive tests, production access, external messages, sensitive data, or material cost.
6. Preserve all attempts and limitations. Do not fix product code, alter tests, weaken an oracle, or synchronize a backlog unless the user separately asks for that action.
7. Finish with the tested scope and revision, methods run, evidence location, confirmed/candidate/not-reproduced findings, gaps, and the next highest-value QA action.

Read [references/lifecycle.md](references/lifecycle.md) when selecting a partial entry point, deciding completion, or resuming an existing session.
