"""Q07: the transcript measurement counts discovery, ledger writes and rejections."""

from __future__ import annotations

import json
import unittest

from scripts.q07_measure import classify, measure


ROOT = "/opt/kit"


def _use(call_id: str, tool: str, **payload: str) -> str:
    content = [{"type": "tool_use", "id": call_id, "name": tool, "input": payload}]
    return json.dumps({"type": "assistant", "message": {"content": content}})


def _result(call_id: str, text: str) -> str:
    content = [{"type": "tool_result", "tool_use_id": call_id, "content": text}]
    return json.dumps({"type": "user", "message": {"content": content}})


class MeasureTests(unittest.TestCase):
    def test_classify_separates_discovery_from_skill_reads_and_writes(self) -> None:
        self.assertEqual({"discovery"}, classify("Bash", {"command": f"python {ROOT}/scripts/qa.py attempt-add --help"}, ROOT))
        self.assertEqual({"discovery"}, classify("Read", {"file_path": f"{ROOT}/examples/session.json"}, ROOT))
        self.assertEqual(set(), classify("Read", {"file_path": f"{ROOT}/skills/qa-session/references/performance.md"}, ROOT))
        self.assertEqual({"ledger_write"}, classify("Bash", {"command": "python3 $Q attempt-add --root . --input a.json s"}, ROOT))
        self.assertEqual(set(), classify("Bash", {"command": f"python {ROOT}/scripts/qa.py summary --root ."}, ROOT))

    def test_measure_counts_rejected_writes_and_usage(self) -> None:
        lines = [
            _use("a", "Read", file_path=f"{ROOT}/src/agentic_qa_kit/model.py"),
            _result("a", "x" * 100),
            _use("b", "Bash", command=f"python {ROOT}/scripts/qa.py finding-add --input f.json s"),
            _result("b", "error: finding.reproduction.attempts must equal"),
            _use("c", "Bash", command=f"python {ROOT}/scripts/qa.py finding-add --input f.json s"),
            _result("c", "{}"),
            json.dumps({"type": "result", "total_cost_usd": 0.5, "usage": {"input_tokens": 3, "cache_read_input_tokens": 7}}),
        ]
        counts = measure(lines, ROOT)
        self.assertEqual((3, 1, 100), (counts["tool_calls"], counts["discovery_calls"], counts["discovery_result_bytes"]))
        self.assertEqual((2, 1), (counts["ledger_writes"], counts["ledger_rejections"]))
        self.assertEqual((10, 0.5), (counts["input_tokens"], counts["cost_usd"]))


if __name__ == "__main__":
    unittest.main()
