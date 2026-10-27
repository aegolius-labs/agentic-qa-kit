"""Run the Q04-G01 functional-design evaluation on the Claude Code lane.

Q04's done-when is that representative specifications produce reviewable
obligation ledgers and tests without presenting model coverage as defect
absence. This lane reuses the Q02 fixtures that carry written rules (a README
or docstring the code must follow) and gives each one fresh headless session
with a prompt that names the specification but not the technique, the
reference, or the ledger fields, so whether the design pack is used at all is
part of what is observed.

On top of Q02's mechanical oracles it reads the obligation ledger the agent
left: whether charters declare obligations, which techniques they use, whether
attempts link to them, and the coverage `summary` would report. Whether the
obligations are faithful to the specification, the oracles independent, and
the report free of a defect-absence claim stays a reviewer's call.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
for entry in (PLUGIN_ROOT, PLUGIN_ROOT / "src"):
    if str(entry) not in sys.path:
        sys.path.insert(0, str(entry))

from agentic_qa_kit.model import obligation_coverage  # noqa: E402
from scripts.q01_claude_code import KIT, LaneError, _plugin_list, _run, child_environment, install_location  # noqa: E402
from scripts.q02_claude_code import load_suite, read_ledger, run_fixture  # noqa: E402

# Q02 fixtures whose behavior is fixed by a written rule.
FIXTURES = ("py-lib", "monorepo", "no-tests")
PROMPT = (
    "Check that this repository's code does what its README and docstrings say it does. "
    "Run one bounded QA session and record its evidence in the QA ledger. Spend no more than "
    "about 20 minutes of work. Stop before any action that needs new authority, and report what "
    "you checked, what you could not check, and why."
)


def obligation_ledger(sessions: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    """What the agent's ledger says about test design, mechanically."""

    obligations = [
        obligation
        for session in sessions
        for charter in session.get("charters", [])
        for obligation in charter.get("obligations") or []
    ]
    linked = sorted(
        {
            obligation_id
            for session in sessions
            for attempt in session.get("attempts", [])
            for obligation_id in attempt.get("obligation_ids") or []
        }
    )
    coverage = {"total": 0, "exercised": 0, "inconclusive": 0, "unexercised": 0}
    for session in sessions:
        for key, value in obligation_coverage(session).items():
            coverage[key] += value
    return {
        "declared": len(obligations),
        "techniques": sorted({obligation["technique"] for obligation in obligations}),
        "linked_obligations": linked,
        "coverage": coverage,
        "obligations": [
            {key: obligation[key] for key in ("id", "technique", "source", "statement", "oracle")}
            for obligation in obligations
        ],
    }


def run_command(args: argparse.Namespace) -> None:
    env = child_environment(args.config_dir)
    kit = install_location(_plugin_list(env), KIT)
    if Path(kit.get("read_from", "")).resolve() != PLUGIN_ROOT:
        raise LaneError("the lane must resolve the plugin in place to this working tree")
    revision = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=PLUGIN_ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()
    wanted = set(args.fixture or FIXTURES)
    fixtures = [f for f in load_suite()["fixtures"] if f["id"] in wanted]
    args.output.mkdir(parents=True, exist_ok=True)

    def one(fixture: Mapping[str, Any]) -> dict[str, Any]:
        record = run_fixture(fixture, PROMPT, args.output, env, runner=_run, timeout=args.timeout)
        sessions, _ = read_ledger(args.output / "targets" / str(fixture["id"]))
        record["design"] = obligation_ledger(sessions)
        return record

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        records = list(pool.map(one, fixtures))
    result = {
        "suite_id": "Q04-G01",
        "lane": "claude-code",
        "surface": "cli",
        "recorded_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "claude_code_version": subprocess.run(
            ["claude", "--version"], env=dict(env), capture_output=True, text=True, check=False
        ).stdout.strip(),
        "plugin_revision": revision,
        "prompt": PROMPT,
        "prompt_sha256": hashlib.sha256(PROMPT.encode("utf-8")).hexdigest(),
        "limitations": [
            "Working-tree provenance: the skills as written at plugin_revision, not a published artifact.",
            "Headless `claude -p` CLI only, one Linux host, one run per fixture.",
            "Three small synthetic fixtures with planted defects stand in for real specifications.",
        ],
        "observations": records,
    }
    (args.output / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(args.output / "result.json"),
                "design": {r["case_id"]: r["design"]["coverage"] for r in records},
                "cost_usd": round(sum(r.get("cost_usd") or 0 for r in records), 2),
            },
            indent=2,
        )
    )


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run the Q04-G01 design evaluation on the Claude Code lane")
    parser.add_argument("--config-dir", type=Path, required=True, help="CLAUDE_CONFIG_DIR with the plugin installed")
    parser.add_argument("--output", type=Path, required=True, help="New directory for targets and results")
    parser.add_argument("--fixture", action="append", choices=FIXTURES, help="Run only this fixture")
    parser.add_argument("--timeout", type=int, default=1500, help="Seconds per session")
    parser.add_argument("--workers", type=int, default=2)
    run_command(parser.parse_args(argv))


if __name__ == "__main__":
    main()
