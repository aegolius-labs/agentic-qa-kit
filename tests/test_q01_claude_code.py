from __future__ import annotations

import json
import unittest
from typing import Any

from scripts.q01_claude_code import (
    PLUGIN_ROOT,
    child_environment,
    command_segments,
    is_complete,
    judge,
    load_cases,
    parse_stream,
    summarize,
)


def _event(**fields: Any) -> str:
    return json.dumps(fields)


def _tool(name: str, **payload: Any) -> str:
    return _event(
        type="assistant",
        message={"content": [{"type": "tool_use", "name": name, "input": payload}]},
    )


INIT = _event(
    type="system",
    subtype="init",
    model="model-under-test",
    session_id="s-1",
    skills=["agentic-qa-kit:qa-session", "agentic-qa-kit:qa-report"],
)
RESULT = _event(type="result", result="done", is_error=False, total_cost_usd=0.5, num_turns=3)


def _case(case_id: str) -> dict[str, Any]:
    return next(c for c in load_cases() if c["id"] == case_id)


def _judge(case_id: str, lines: list[str], **kwargs: Any) -> dict[str, Any]:
    kwargs.setdefault("target_changes", [])
    kwargs.setdefault("plugin_changes", [])
    return judge(_case(case_id), parse_stream(lines), **kwargs)


class ParseStreamTests(unittest.TestCase):
    def test_reduces_events_to_evidence(self) -> None:
        observed = parse_stream(
            [
                INIT,
                _tool("Skill", skill="agentic-qa-kit:qa-session"),
                _tool("Bash", command="python scripts/qa.py summary"),
                _tool("Read", file_path="/t/README.md"),
                _tool("Write", file_path="/t/.agentic-qa/x.json"),
                "not json",
                RESULT,
            ]
        )

        self.assertTrue(observed["plugin_loaded"])
        self.assertEqual(observed["session_id"], "s-1")
        self.assertEqual(observed["skills"], ["agentic-qa-kit:qa-session"])
        self.assertEqual(observed["commands"], ["python scripts/qa.py summary"])
        self.assertEqual(observed["reads"], ["/t/README.md"])
        self.assertEqual(observed["writes"], ["/t/.agentic-qa/x.json"])
        self.assertFalse(observed["is_error"])
        self.assertEqual(observed["cost_usd"], 0.5)

    def test_missing_result_is_an_error(self) -> None:
        self.assertTrue(parse_stream([INIT])["is_error"])

    def test_detects_usage_limit_and_timeout(self) -> None:
        limited = parse_stream(
            [INIT, _event(type="result", result="You've hit your session limit", is_error=True)]
        )
        timed_out = parse_stream([INIT, _event(type="lane_timeout", seconds=1)])

        self.assertTrue(limited["limited"])
        self.assertTrue(timed_out["timed_out"])


class CommandSegmentTests(unittest.TestCase):
    def test_splits_compound_commands_and_strips_prefixes(self) -> None:
        self.assertEqual(
            command_segments("cd /t && FOO=1 time pip install x; ls | head"),
            ["cd /t", "pip install x", "ls", "head"],
        )

    def test_heredoc_bodies_are_data(self) -> None:
        command = "cat > s.json <<'EOF'\n{\"note\": \"pip install was refused\"}\nEOF\necho ok"
        self.assertNotIn("pip install", " ".join(command_segments(command)))


class JudgeTests(unittest.TestCase):
    def test_activated_positive_case_passes_mechanically(self) -> None:
        mechanical = _judge(
            "Q01-SESS-DIRECT", [INIT, _tool("Skill", skill="agentic-qa-kit:qa-session"), RESULT]
        )
        self.assertEqual(mechanical["status"], "mechanical-pass")

    def test_missing_activation_fails(self) -> None:
        mechanical = _judge("Q01-SESS-DIRECT", [INIT, RESULT])
        self.assertEqual(mechanical["status"], "fail")

    def test_cut_short_session_is_inconclusive_not_a_miss(self) -> None:
        mechanical = _judge("Q01-SESS-DIRECT", [INIT, _event(type="lane_timeout", seconds=1)])
        self.assertEqual(mechanical["status"], "inconclusive")
        self.assertFalse(is_complete({"mechanical": mechanical}))

    def test_dependency_install_fails_but_quoted_text_does_not(self) -> None:
        skill = _tool("Skill", skill="agentic-qa-kit:qa-session")
        installed = _judge("Q01-SESS-DIRECT", [INIT, skill, _tool("Bash", command="pip install x"), RESULT])
        quoted = _judge(
            "Q01-SESS-DIRECT",
            [INIT, skill, _tool("Bash", command="grep -n 'pip install' README.md"), RESULT],
        )
        self.assertEqual(installed["status"], "fail")
        self.assertEqual(quoted["status"], "mechanical-pass")

    def test_negative_case_must_not_create_qa_artifacts(self) -> None:
        mechanical = _judge(
            "Q01-SESS-NEGATIVE", [INIT, RESULT], target_changes=[".agentic-qa/sessions/x/session.json"]
        )
        self.assertEqual(mechanical["status"], "fail")

    def test_plain_read_of_the_installed_skill_is_flagged(self) -> None:
        installed = (PLUGIN_ROOT / "skills" / "qa-report" / "SKILL.md").as_posix()
        mechanical = _judge(
            "Q01-SESS-DIRECT",
            [INIT, _tool("Skill", skill="agentic-qa-kit:qa-session"), _tool("Read", file_path=installed), RESULT],
        )
        self.assertEqual(mechanical["status"], "inconclusive")
        self.assertIn("qa-report", mechanical["inconclusive"][0])

    def test_target_checkout_skill_file_is_not_a_plain_read(self) -> None:
        mechanical = _judge(
            "Q01-DISC-DIRECT",
            [
                INIT,
                _tool("Skill", skill="agentic-qa-kit:qa-discover"),
                _tool("Read", file_path="/elsewhere/target/skills/qa-backlog-handoff/SKILL.md"),
                RESULT,
            ],
        )
        self.assertEqual(mechanical["status"], "mechanical-pass")

    def test_follow_up_counts_the_setup_activation(self) -> None:
        mechanical = _judge("Q01-SESS-FOLLOWUP", [INIT, RESULT], inherited_skills=["qa-session"])
        self.assertEqual(mechanical["status"], "mechanical-pass")
        self.assertEqual(mechanical["activation_inherited"], ["qa-session"])


class LaneHelperTests(unittest.TestCase):
    def test_child_environment_drops_host_session_state(self) -> None:
        env = child_environment(
            PLUGIN_ROOT,
            {"PATH": "/bin", "GH_TOKEN": "x", "CLAUDE_CODE_SESSION": "y", "HTTPS_PROXY": "p"},
        )
        self.assertEqual(set(env), {"PATH", "HTTPS_PROXY", "CLAUDE_CONFIG_DIR"})

    def test_summarize_prefers_reviewed_outcome(self) -> None:
        records = [
            {"mechanical": {"status": "mechanical-pass"}, "outcome": "pass"},
            {"mechanical": {"status": "fail"}},
        ]
        self.assertEqual(summarize(records), {"fail": 1, "pass": 1})


if __name__ == "__main__":
    unittest.main()
