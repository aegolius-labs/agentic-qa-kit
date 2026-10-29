"""Measure what Q07 asks about from retained lane transcripts.

Q07 decides whether host tools plus the local ledger leave authorization,
compact-query, portability or structured-result gaps that an MCP server would
close. This reads `claude -p --output-format stream-json` transcripts kept by
the Q02, Q04 and Q05 lanes and counts, per session:

- tool calls, and the calls spent learning the ledger's payload shapes: reading
  the plugin's `src/`, `examples/`, `templates/`, `schemas/`, `docs/` or
  README, or calling `qa.py ... --help`. Skill and reference reads are the
  intended route and are not counted as discovery;
- the bytes those calls returned, a proxy for the context they cost;
- ledger writes through `qa.py`, and how many the CLI rejected;
- the session's total input tokens and cost, from the transcript's result line.

It reads transcripts only and writes one JSON summary. The judgment of what
the numbers mean stays in the decision record.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


WRITES = ("init", "session-create", "attempt-add", "finding-add", "finding-update", "session-close", "migrate")
_DISCOVERY_PATHS = re.compile(r"/(src|examples|templates|schemas|docs)/|README|CONTRIBUTING")
_HELP = re.compile(r"qa\.py\b[^;&|\n]*--help")
_WRITE = re.compile(r"(?:qa\.py|\$\{?\w+\}?)\s+(" + "|".join(WRITES) + r")\b(?![^;&|\n]*--help)")


def _text(content: Any) -> str:
    if isinstance(content, str):
        return content
    return json.dumps(content, ensure_ascii=False)


def classify(tool: str, payload: Mapping[str, Any], plugin_root: str) -> set[str]:
    """Which of `discovery` and `ledger_write` a tool call is."""

    text = _text(payload)
    kinds: set[str] = set()
    if tool == "Bash":
        command = str(payload.get("command", ""))
        if _HELP.search(command):
            kinds.add("discovery")
        elif plugin_root in command and _DISCOVERY_PATHS.search(command.split(plugin_root, 1)[1]):
            kinds.add("discovery")
        if _WRITE.search(command):
            kinds.add("ledger_write")
    elif tool in {"Read", "Grep", "Glob"} and plugin_root in text:
        after = text.split(plugin_root, 1)[1]
        if _DISCOVERY_PATHS.search(after) and "/skills/" not in after:
            kinds.add("discovery")
    return kinds


def measure(lines: Iterable[str], plugin_root: str) -> dict[str, Any]:
    calls: dict[str, set[str]] = {}
    counts = {"tool_calls": 0, "discovery_calls": 0, "discovery_result_bytes": 0, "result_bytes": 0,
              "ledger_writes": 0, "ledger_rejections": 0}
    final: Mapping[str, Any] = {}
    for line in lines:
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "result":
            final = event
        message = event.get("message")
        content = message.get("content") if isinstance(message, dict) else None
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "tool_use":
                kinds = classify(str(block.get("name")), block.get("input") or {}, plugin_root)
                calls[block["id"]] = kinds
                counts["tool_calls"] += 1
                counts["discovery_calls"] += "discovery" in kinds
                counts["ledger_writes"] += "ledger_write" in kinds
            elif block.get("type") == "tool_result":
                kinds = calls.get(str(block.get("tool_use_id")), set())
                size = len(_text(block.get("content")).encode("utf-8"))
                counts["result_bytes"] += size
                if "discovery" in kinds:
                    counts["discovery_result_bytes"] += size
                if "ledger_write" in kinds and "error:" in _text(block.get("content")):
                    counts["ledger_rejections"] += 1
    usage = final.get("usage") or {}
    counts["input_tokens"] = sum(int(usage.get(key) or 0) for key in
                                 ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
    counts["cost_usd"] = round(float(final.get("total_cost_usd") or 0), 4)
    counts["permission_denials"] = len(final.get("permission_denials") or [])
    return counts


def summarize(per_session: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    total = {key: sum(s[key] for s in per_session.values()) for key in next(iter(per_session.values()))}
    total["cost_usd"] = round(total["cost_usd"], 2)
    total["sessions"] = len(per_session)
    total["sessions_with_discovery"] = sum(1 for s in per_session.values() if s["discovery_calls"])
    total["discovery_call_share"] = round(total["discovery_calls"] / max(total["tool_calls"], 1), 3)
    total["discovery_byte_share"] = round(total["discovery_result_bytes"] / max(total["result_bytes"], 1), 3)
    return total


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="Measure Q07 inputs from retained lane transcripts")
    parser.add_argument("raw", nargs="+", type=Path, help="Directories of <case>.jsonl transcripts")
    parser.add_argument("--plugin-root", required=True, help="The plugin path as it appears in the transcripts")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)
    per_session = {}
    for directory in args.raw:
        for path in sorted(directory.glob("*.jsonl")):
            key = f"{directory.parent.name}/{path.stem}"
            per_session[key] = measure(path.read_text(encoding="utf-8").splitlines(), args.plugin_root)
    result = {"total": summarize(per_session), "sessions": per_session}
    text = json.dumps(result, indent=2) + "\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    print(json.dumps(result["total"], indent=2))


if __name__ == "__main__":
    main()
