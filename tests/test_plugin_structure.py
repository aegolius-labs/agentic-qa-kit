from __future__ import annotations

import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PluginStructureTests(unittest.TestCase):
    def test_manifest_and_skill_names_match(self) -> None:
        manifest = json.loads((ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["name"], "agentic-qa-kit")
        self.assertEqual(manifest["skills"], "./skills/")
        expected = {
            "qa-workflow",
            "qa-discover",
            "qa-session",
            "qa-reproduce",
            "qa-report",
            "qa-backlog-handoff",
        }
        self.assertEqual({path.name for path in (ROOT / "skills").iterdir() if path.is_dir()}, expected)

    def test_skills_have_no_scaffold_placeholders(self) -> None:
        for skill in (ROOT / "skills").iterdir():
            text = (skill / "SKILL.md").read_text(encoding="utf-8")
            self.assertNotIn("[TODO", text)
            self.assertIn(f"name: {skill.name}", text)
            metadata = (skill / "agents" / "openai.yaml").read_text(encoding="utf-8")
            self.assertIn(f"${skill.name}", metadata)


if __name__ == "__main__":
    unittest.main()
