"""Run the Q12 escape-driven discovery evaluation on the Claude Code lane.

Q12's done-when is that a QA round planned after an incident names the check
that missed it, adds a regression charter whose oracle is the observed
failure and that cites the incident, keeps the incident's personal data out of
the ledger, and runs nothing it was not asked to run. This lane stages the one
fixture in `evals/q12-fixtures.json`, a small library with a postmortem under
`docs/`, in fresh sessions.

On top of Q02's mechanical oracles it records whether the session read
`qa-discover`'s escapes reference, fails the run if any of the fixture's
personal data appears under `.agentic-qa/`, counts recorded attempts (a plan
should have none), and reports which charters cite the incident and which
planted-defect keywords the plan or answer names. Whether the charter is the
right one stays a reviewer's call.
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

from scripts.q01_claude_code import KIT, LaneError, _plugin_list, _run, child_environment, install_location, parse_stream  # noqa: E402
from scripts.q02_claude_code import load_suite, read_ledger, run_fixture  # noqa: E402
from scripts.q05_claude_code import SUFFIX  # noqa: E402

SUITE = PLUGIN_ROOT / "evals" / "q12-fixtures.json"
REFERENCE = "qa-discover/references/escapes.md"
INCIDENT_WORDS = ("postmortem", "incident", "2026-09-18", "escape")


def read_reference(stdout: str) -> bool:
    observed = parse_stream(stdout.splitlines())
    return any(REFERENCE in text for text in [*observed["reads"], *observed["commands"]])


def leaked_personal_data(fixture: Mapping[str, Any], target: Path) -> list[str]:
    """Personal data from the fixture that appears anywhere under the target's `.agentic-qa/`."""

    control = target / ".agentic-qa"
    texts = [p.read_text(encoding="utf-8", errors="replace") for p in control.rglob("*") if p.is_file()]
    blob = "\n".join(texts).lower()
    return [value for value in fixture.get("personal_data", []) if value.lower() in blob]


def plan_facts(fixture: Mapping[str, Any], sessions: Sequence[Mapping[str, Any]], answer: str) -> dict[str, Any]:
    charters = [c for s in sessions for c in s.get("charters") or []]
    citing = [
        c.get("id")
        for c in charters
        if any(word in json.dumps(c.get("risks") or []).lower() for word in INCIDENT_WORDS)
    ]
    haystack = (json.dumps(charters) + "\n" + answer).lower()
    return {
        "charters": len(charters),
        "charters_citing_incident": citing,
        "attempts": sum(len(s.get("attempts") or []) for s in sessions),
        "defects_named": {
            d["id"]: [w for w in d["keywords"] if w.lower() in haystack] for d in fixture.get("planted_defects", [])
        },
    }


def run_command(args: argparse.Namespace) -> None:
    env = child_environment(args.config_dir)
    kit = install_location(_plugin_list(env), KIT)
    if Path(kit.get("read_from", "")).resolve() != PLUGIN_ROOT:
        raise LaneError("the lane must resolve the plugin in place to this working tree")
    revision = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=PLUGIN_ROOT, capture_output=True, text=True, check=True
    ).stdout.strip()
    suite = load_suite(SUITE)
    prompt = suite["prompt"] + SUFFIX
    args.output.mkdir(parents=True, exist_ok=True)
    cases = [
        {**fixture, "id": f"{fixture['id']}-{repeat}", "fixture": fixture["id"]}
        for fixture in suite["fixtures"]
        for repeat in range(1, args.repeats + 1)
    ]

    def one(case: Mapping[str, Any]) -> dict[str, Any]:
        record = run_fixture(case, prompt, args.output, env, runner=_run, timeout=args.timeout)
        target = args.output / "targets" / case["id"]
        stdout = (args.output / "raw" / f"{case['id']}.jsonl").read_text(encoding="utf-8")
        sessions, _ = read_ledger(target)
        leaked = leaked_personal_data(case, target)
        if leaked:
            record["mechanical"]["failures"].append(f"personal data from the incident is in the ledger: {leaked}")
            record["mechanical"]["status"] = "fail"
        record.update(
            fixture=case["fixture"],
            escapes_reference_read=read_reference(stdout),
            plan=plan_facts(case, sessions, record["answer"]),
        )
        return record

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        records = list(pool.map(one, cases))
    result = {
        "suite_id": "Q12-G01",
        "lane": "claude-code",
        "surface": "cli",
        "recorded_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "claude_code_version": subprocess.run(
            ["claude", "--version"], env=dict(env), capture_output=True, text=True, check=False
        ).stdout.strip(),
        "plugin_revision": revision,
        "prompt": prompt,
        "prompt_sha256": hashlib.sha256(prompt.encode("utf-8")).hexdigest(),
        "limitations": [
            "Working-tree provenance: the skills as written at plugin_revision, not a published artifact.",
            "Headless `claude -p` CLI only, one Linux host.",
            "One small synthetic fixture and postmortem; keyword hits are discovery aids, not verdicts.",
        ],
        "observations": records,
    }
    (args.output / "result.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(
        json.dumps(
            {
                "output": str(args.output / "result.json"),
                "cases": {
                    r["case_id"]: {
                        "status": r["mechanical"].get("status"),
                        "escapes_read": r["escapes_reference_read"],
                        "plan": r["plan"],
                    }
                    for r in records
                },
                "cost_usd": round(sum(r.get("cost_usd") or 0 for r in records), 2),
            },
            indent=2,
        )
    )


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run the Q12 escape-driven discovery evaluation on the Claude Code lane")
    parser.add_argument("--config-dir", type=Path, required=True, help="CLAUDE_CONFIG_DIR with the plugin installed")
    parser.add_argument("--output", type=Path, required=True, help="New directory for targets and results")
    parser.add_argument("--repeats", type=int, default=2, help="Fresh sessions per fixture")
    parser.add_argument("--timeout", type=int, default=1500, help="Seconds per session")
    parser.add_argument("--workers", type=int, default=2)
    run_command(parser.parse_args(argv))


if __name__ == "__main__":
    main()
