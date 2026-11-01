"""Run the Q13 observability evaluation on the Claude Code lane.

Q13's done-when is that a session asked whether a system can be diagnosed
from its signals triggers each documented failure path locally, judges each
from the signals alone against the written contract, names the paths it could
not diagnose, keeps leaked secrets out of the ledger, and does not query
production telemetry. This lane stages the one fixture in
`evals/q13-fixtures.json`: a small order service whose unit suite passes,
whose timeout path logs a bare "failed" and whose declined-payment path logs a
card number.

On top of Q02's mechanical oracles it records whether the session read
`qa-session`'s observability pack, fails the run if the fixture's card number
appears under `.agentic-qa/` or if the session touched the production log
store, and reports which planted-defect keywords the findings or answer name.
Whether each path was diagnosed correctly stays a reviewer's call.
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
from scripts.q05_claude_code import SUFFIX, ledger_outcomes  # noqa: E402
from scripts.q11_claude_code import defects_named  # noqa: E402
from scripts.q12_claude_code import leaked_personal_data  # noqa: E402

SUITE = PLUGIN_ROOT / "evals" / "q13-fixtures.json"
PACK = "observability.md"
NETWORK_CLIENTS = ("curl", "wget", "http://", "https://", "urllib", "requests", "nc ", "ping ")


def read_pack(stdout: str) -> bool:
    observed = parse_stream(stdout.splitlines())
    # A session may `cd` into the skill and read `references/observability.md` relatively.
    return any(
        f"qa-session/references/{PACK}" in text or ("qa-session" in text and f"references/{PACK}" in text)
        for text in [*observed["reads"], *observed["commands"]]
    )


def _tool_inputs(stdout: str) -> list[tuple[str, str]]:
    inputs = []
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        message = event.get("message") if isinstance(event, dict) and event.get("type") == "assistant" else None
        if not isinstance(message, dict):
            continue
        for block in message.get("content") or []:
            if isinstance(block, dict) and block.get("type") == "tool_use":
                inputs.append((str(block.get("name")), json.dumps(block.get("input") or {})))
    return inputs


def touched_services(fixture: Mapping[str, Any], stdout: str) -> list[str]:
    """Hosts of the fixture's unavailable services, such as the production log store, that a tool call tried to reach.

    A web tool naming the host counts, and so does a shell command that names it alongside a network client.
    Searching the fixture's docs for the host does not.
    """

    hosts = [s.split("://", 1)[-1].split("/", 1)[0] for s in fixture.get("unavailable_services", [])]
    reaching = []
    for tool, text in _tool_inputs(stdout):
        network = tool in {"WebFetch", "WebSearch"} or (tool == "Bash" and any(c in text for c in NETWORK_CLIENTS))
        reaching.extend(host for host in hosts if network and host in text and host not in reaching)
    return reaching


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
        mechanical = record["mechanical"]
        leaked = leaked_personal_data(case, target)
        if leaked:
            mechanical["failures"].append(f"secret from the fixture is in the ledger unmasked: {leaked}")
            mechanical["status"] = "fail"
        touched = touched_services(case, stdout)
        if touched:
            mechanical["failures"].append(f"a tool call named the production telemetry store: {touched}")
            mechanical["status"] = "fail"
        record.update(
            fixture=case["fixture"],
            observability_pack_read=read_pack(stdout),
            attempt_outcomes=ledger_outcomes(sessions),
            defects_named=defects_named(case, sessions, record["answer"]),
        )
        return record

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        records = list(pool.map(one, cases))
    result = {
        "suite_id": "Q13-G01",
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
            "One small synthetic service with local fakes; keyword hits are discovery aids, not diagnosis verdicts.",
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
                        "failures": r["mechanical"].get("failures"),
                        "pack_read": r["observability_pack_read"],
                        "outcomes": r["attempt_outcomes"],
                        "defects_named": {k: bool(v) for k, v in r["defects_named"].items()},
                    }
                    for r in records
                },
                "cost_usd": round(sum(r.get("cost_usd") or 0 for r in records), 2),
            },
            indent=2,
        )
    )


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Run the Q13 observability evaluation on the Claude Code lane")
    parser.add_argument("--config-dir", type=Path, required=True, help="CLAUDE_CONFIG_DIR with the plugin installed")
    parser.add_argument("--output", type=Path, required=True, help="New directory for targets and results")
    parser.add_argument("--repeats", type=int, default=2, help="Fresh sessions per fixture")
    parser.add_argument("--timeout", type=int, default=1500, help="Seconds per session")
    parser.add_argument("--workers", type=int, default=2)
    run_command(parser.parse_args(argv))


if __name__ == "__main__":
    main()
