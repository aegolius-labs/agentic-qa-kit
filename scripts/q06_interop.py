"""Q06: check the QA-to-backlog handoff against a real Agentic Backlog Kit.

The run is offline. It stages the deterministic Q01 evidence fixture in a fresh
directory, exports its confirmed finding, and feeds the payload to the sibling
kit's `item-add`. The only backlog commands it calls are `item-add`, `validate`
and `show`, which read and write the local manifest; GitHub credentials are
removed from their environment, so no synchronization can happen.

Each check records what was expected, what was observed, and whether it held.
A failed check is a finding about the two kits, not a failure of this script.

    python scripts/q06_interop.py --backlog-kit ../agentic-backlog-kit
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any


PLUGIN_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PLUGIN_ROOT / "src"
for path in (SRC_ROOT, PLUGIN_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))

from agentic_qa_kit.store import KitStore, atomic_write_json  # noqa: E402
from scripts.q01_fixture import stage_fixture  # noqa: E402

QA = PLUGIN_ROOT / "scripts" / "qa.py"
SCRUBBED = ("GH_TOKEN", "GITHUB_TOKEN", "GH_ENTERPRISE_TOKEN", "GITHUB_ENTERPRISE_TOKEN")


def default_backlog_kit() -> Path | None:
    configured = os.environ.get("AGENTIC_BACKLOG_KIT")
    candidate = Path(configured) if configured else PLUGIN_ROOT.parent / "agentic-backlog-kit"
    return candidate.resolve() if (candidate / "scripts" / "backlog.py").is_file() else None


def _run(command: list[str], cwd: Path) -> dict[str, Any]:
    env = {key: value for key, value in os.environ.items() if key not in SCRUBBED}
    completed = subprocess.run(command, cwd=cwd, env=env, capture_output=True, text=True, check=False)
    try:
        output: Any = json.loads(completed.stdout)
    except json.JSONDecodeError:
        output = completed.stdout.strip()
    return {"exit": completed.returncode, "output": output, "stderr": completed.stderr.strip()[-400:]}


def _sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _check(checks: list[dict[str, Any]], check_id: str, expectation: str, held: bool, observed: Any) -> None:
    checks.append({"id": check_id, "expectation": expectation, "held": held, "observed": observed})


def _add_candidate_session(store: KitStore) -> None:
    confirmed = store.load_session("q01-fixture")
    session = {
        key: confirmed[key] for key in ("objective", "mode", "target", "scope", "context", "charters")
    }
    session["id"] = "q06-candidate"
    session["charters"] = [{**confirmed["charters"][0], "status": "planned"}]
    store.create_session(session)
    attempt = {**confirmed["attempts"][0], "id": "attempt-candidate"}
    attempt.pop("evidence")
    store.add_attempt("q06-candidate", attempt)
    finding = {**confirmed["findings"][0], "id": "F-CANDIDATE", "status": "candidate"}
    finding["attempt_ids"] = ["attempt-candidate"]
    finding["evidence"] = []
    store.add_finding("q06-candidate", finding)


def run(backlog_kit: Path, workdir: Path) -> dict[str, Any]:
    abk = [sys.executable, str(backlog_kit / "scripts" / "backlog.py")]
    qa = [sys.executable, str(QA)]
    target = workdir / "target"
    staged = stage_fixture(target)
    store = KitStore(target)
    _add_candidate_session(store)
    fields_path = Path(staged["planning_fields"])
    fields = json.loads(fields_path.read_text(encoding="utf-8"))
    manifest = Path(staged["backlog_manifest"])
    ledger_before = {str(path.relative_to(target)): _sha(path) for path in (target / ".agentic-qa").rglob("session.json")}
    checks: list[dict[str, Any]] = []

    bug_path = workdir / "bug.json"
    exported = _run([*qa, "backlog-export", "--root", str(target), "q01-fixture", "F-001",
                     "--input", str(fields_path), "--output", str(bug_path)], target)
    _check(checks, "I1-export-confirmed", "A confirmed finding exports one Bug payload.",
           exported["exit"] == 0 and json.loads(bug_path.read_text(encoding="utf-8"))["type"] == "Bug",
           exported["output"])

    candidate = _run([*qa, "backlog-export", "--root", str(target), "q06-candidate", "F-CANDIDATE",
                      "--input", str(fields_path)], target)
    _check(checks, "I2-reject-candidate", "A candidate finding is refused.",
           candidate["exit"] != 0 and "confirmed" in candidate["stderr"], candidate["stderr"])

    partial_path = workdir / "partial-fields.json"
    atomic_write_json(partial_path, {key: value for key, value in fields.items() if key != "impact"})
    partial = _run([*qa, "backlog-export", "--root", str(target), "q01-fixture", "F-001",
                    "--input", str(partial_path)], target)
    _check(checks, "I3-no-guessed-inputs", "Missing planning input is refused, never defaulted.",
           partial["exit"] != 0 and "impact" in partial["stderr"], partial["stderr"])

    foreign_path = workdir / "foreign-status-fields.json"
    atomic_write_json(foreign_path, {**fields, "status": "Backlog"})
    foreign_bug = workdir / "foreign-status-bug.json"
    _run([*qa, "backlog-export", "--root", str(target), "q01-fixture", "F-001",
          "--input", str(foreign_path), "--output", str(foreign_bug)], target)
    before = _sha(manifest)
    foreign = _run([*abk, "item-add", "--input", str(foreign_bug)], target)
    _check(checks, "I4-status-from-backlog-workflow",
           "A status outside the backlog manifest's workflow is refused and changes nothing.",
           foreign["exit"] != 0 and _sha(manifest) == before, foreign["output"] or foreign["stderr"])

    added = _run([*abk, "item-add", "--input", str(bug_path)], target)
    item_id = added["output"].get("item_id") if isinstance(added["output"], dict) else None
    shown = _run([*abk, "show", item_id], target) if item_id else {"output": None}
    valid = _run([*abk, "validate"], target)
    item = (shown["output"] or {}).get("item", {}) if isinstance(shown["output"], dict) else {}
    description = item.get("description", "")
    linked = all(text in description for text in ("`q01-fixture`", "`F-001`", "`q01-fixture-revision`", "sha256:"))
    _check(checks, "I5-ingest-links-evidence",
           "Ingestion yields a valid Bug whose description links the QA session, finding, revision and evidence digest.",
           added["exit"] == 0 and valid["exit"] == 0 and item.get("type") == "Bug" and linked,
           {"item_id": item_id, "type": item.get("type"), "linked": linked})

    ledger_after = {str(path.relative_to(target)): _sha(path) for path in (target / ".agentic-qa").rglob("session.json")}
    _check(checks, "I6-qa-ledger-untouched", "Handoff and ingestion leave the QA ledger unchanged.",
           ledger_before == ledger_after, sorted(ledger_after))

    before = _sha(manifest)
    repeat = _run([*abk, "item-add", "--input", str(bug_path)], target)
    _check(checks, "I7-no-duplicate-ingest", "Ingesting the same finding again is refused and changes nothing.",
           repeat["exit"] != 0 and _sha(manifest) == before, repeat["output"])

    summary = _run([*abk, "summary"], target)
    return {
        "suite": "Q06",
        "backlog_kit_revision": _revision(backlog_kit),
        "qa_kit_revision": _revision(PLUGIN_ROOT),
        "backlog_commands": ["item-add", "validate", "show", "summary"],
        "github_credentials_removed": list(SCRUBBED),
        "checks": checks,
        "backlog_summary": summary["output"],
        "held": sum(1 for check in checks if check["held"]),
        "failed": [check["id"] for check in checks if not check["held"]],
    }


def _revision(root: Path) -> str:
    completed = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, capture_output=True, text=True, check=False)
    return completed.stdout.strip() or "unknown"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--backlog-kit", type=Path, default=default_backlog_kit())
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    if args.backlog_kit is None:
        parser.error("no Agentic Backlog Kit found; pass --backlog-kit or set AGENTIC_BACKLOG_KIT")
    with tempfile.TemporaryDirectory() as temporary:
        result = run(args.backlog_kit.resolve(), Path(temporary))
    text = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
