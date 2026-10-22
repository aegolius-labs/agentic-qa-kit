from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .backlog import build_backlog_item
from .model import ValidationError, read_json
from .receipts import integrity
from .store import KitStore, atomic_write_json


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="aqk", description="Agentic QA Kit evidence ledger")
    subparsers = parser.add_subparsers(dest="command", required=True)

    def with_root(command: argparse.ArgumentParser) -> None:
        command.add_argument("--root", default=".", help="Target repository root (default: current directory)")

    init = subparsers.add_parser("init", help="Initialize .agentic-qa/manifest.json")
    with_root(init)
    init.add_argument("--force", action="store_true", help="Replace an existing manifest")

    validate = subparsers.add_parser("validate", help="Validate the manifest and all sessions")
    with_root(validate)

    create = subparsers.add_parser("session-create", help="Create a validated QA session")
    with_root(create)
    create.add_argument("--input", required=True, help="Session JSON input")

    attempt = subparsers.add_parser("attempt-add", help="Append an attempt to a session")
    with_root(attempt)
    attempt.add_argument("session_id")
    attempt.add_argument("--input", required=True, help="Attempt JSON input")

    finding_add = subparsers.add_parser("finding-add", help="Append a finding to a session")
    with_root(finding_add)
    finding_add.add_argument("session_id")
    finding_add.add_argument("--input", required=True, help="Finding JSON input")

    finding_update = subparsers.add_parser("finding-update", help="Update and transition a finding")
    with_root(finding_update)
    finding_update.add_argument("session_id")
    finding_update.add_argument("finding_id")
    finding_update.add_argument("--input", required=True, help="Finding patch JSON input")

    close = subparsers.add_parser("session-close", help="Close a session as completed or blocked")
    with_root(close)
    close.add_argument("session_id")
    close.add_argument("--status", required=True, choices=["completed", "blocked"])
    close.add_argument("--input", required=True, help="Decision JSON input")

    summary = subparsers.add_parser("summary", help="Show a compact session summary")
    with_root(summary)
    summary.add_argument("--session", help="Limit to one session ID")

    show = subparsers.add_parser("show", help="Show one session or finding")
    with_root(show)
    show.add_argument("session_id")
    show.add_argument("--finding", help="Show only one finding ID")

    migrate = subparsers.add_parser("migrate", help="Seal a schema-version-1 session with a receipt chain")
    with_root(migrate)
    migrate.add_argument("session_id")

    export = subparsers.add_parser("backlog-export", help="Export a confirmed finding as a backlog Bug payload")
    with_root(export)
    export.add_argument("session_id")
    export.add_argument("finding_id")
    export.add_argument("--input", required=True, help="Explicit backlog planning fields JSON")
    export.add_argument("--output", help="Write payload atomically instead of stdout")

    return parser


def _print(payload: Any) -> None:
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def _session_summary(session: dict[str, Any]) -> dict[str, Any]:
    counts: dict[str, int] = {}
    for finding in session["findings"]:
        counts[finding["status"]] = counts.get(finding["status"], 0) + 1
    return {
        "id": session["id"],
        "objective": session["objective"],
        "mode": session["mode"],
        "status": session["status"],
        "revision": session["target"]["revision"],
        "dirty": session["target"]["dirty"],
        "charters": len(session["charters"]),
        "attempts": len(session["attempts"]),
        "findings": counts,
        "gaps": len(session["gaps"]),
        "integrity": integrity(session),
    }


def run(args: argparse.Namespace) -> Any:
    store = KitStore(args.root)
    if args.command == "init":
        return {"manifest": str(store.initialize(force=args.force))}
    if args.command == "validate":
        return {"valid": True, **store.validate_all()}
    if args.command == "session-create":
        return store.create_session(read_json(Path(args.input)))
    if args.command == "attempt-add":
        return store.add_attempt(args.session_id, read_json(Path(args.input)))
    if args.command == "finding-add":
        return store.add_finding(args.session_id, read_json(Path(args.input)))
    if args.command == "finding-update":
        return store.update_finding(args.session_id, args.finding_id, read_json(Path(args.input)))
    if args.command == "session-close":
        return store.close_session(args.session_id, args.status, read_json(Path(args.input)))
    if args.command == "summary":
        sessions = [store.load_session(args.session)] if args.session else store.list_sessions()
        return {"sessions": [_session_summary(session) for session in sessions]}
    if args.command == "show":
        session = store.load_session(args.session_id)
        if args.finding:
            finding = next((item for item in session["findings"] if item["id"] == args.finding), None)
            if finding is None:
                raise ValidationError(f"unknown finding ID: {args.finding}")
            return finding
        # Receipts grow with every write; resume needs only their verdict.
        shown = {key: value for key, value in session.items() if key != "receipts"}
        shown["integrity"] = {"status": integrity(session), "receipts": len(session.get("receipts") or [])}
        return shown
    if args.command == "migrate":
        session = store.migrate_session(args.session_id)
        return {"session": session["id"], "schema_version": session["schema_version"], "integrity": integrity(session)}
    if args.command == "backlog-export":
        session = store.load_session(args.session_id)
        finding = next((item for item in session["findings"] if item["id"] == args.finding_id), None)
        if finding is None:
            raise ValidationError(f"unknown finding ID: {args.finding_id}")
        payload = build_backlog_item(session, finding, read_json(Path(args.input)))
        if args.output:
            output = Path(args.output).resolve()
            atomic_write_json(output, payload)
            return {"output": str(output), "type": "Bug", "finding": finding["id"]}
        return payload
    raise AssertionError(f"unhandled command: {args.command}")


def main(argv: list[str] | None = None) -> None:
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        result = run(args)
    except ValidationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    _print(result)
