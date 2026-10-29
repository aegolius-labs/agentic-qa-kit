"""Q05: each non-functional pack states what its done-when requires and fails closed."""

from __future__ import annotations

import re
import unittest
from pathlib import Path

from agentic_qa_kit.model import QUALITY_ATTRIBUTES


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "qa-session"
PACKS = {
    "performance.md": {"performance-efficiency"},
    "resilience.md": {"reliability"},
    "accessibility-i18n.md": {"interaction-capability", "compatibility"},
    "data-integrity.md": {"data-integrity"},
}
# Workload, threat or population; environment; oracle; uncertainty; stop
# conditions; evidence. The first heading varies with what the pack scopes.
SCOPE_HEADINGS = {"Workload", "Fault model", "Population and scope", "Population and claim"}
REQUIRED_HEADINGS = ["Environment", "Oracle", "Uncertainty", "Stop conditions", "Evidence"]


def _headings(text: str) -> list[str]:
    return re.findall(r"^## (.+)$", text, flags=re.MULTILINE)


class NonFunctionalPackTests(unittest.TestCase):
    def test_every_pack_states_the_done_when_sections_in_order(self) -> None:
        for name in PACKS:
            with self.subTest(pack=name):
                headings = _headings((SKILL / "references" / name).read_text(encoding="utf-8"))
                self.assertEqual("Authority: fail closed", headings[0])
                self.assertIn(headings[1], SCOPE_HEADINGS)
                self.assertEqual(REQUIRED_HEADINGS, headings[2:])

    def test_every_pack_fails_closed_to_inconclusive(self) -> None:
        for name in PACKS:
            with self.subTest(pack=name):
                text = (SKILL / "references" / name).read_text(encoding="utf-8")
                authority = text.split("## ", 2)[1]
                self.assertRegex(authority, r"needs? (its|their) own approval")
                self.assertIn("`inconclusive` and stop", authority)

    def test_packs_name_real_quality_attributes(self) -> None:
        for name, attributes in PACKS.items():
            with self.subTest(pack=name):
                self.assertTrue(attributes <= QUALITY_ATTRIBUTES)
                text = (SKILL / "references" / name).read_text(encoding="utf-8")
                for attribute in attributes:
                    self.assertIn(f"`{attribute}`", text)

    def test_the_skill_routes_to_every_pack(self) -> None:
        body = (SKILL / "SKILL.md").read_text(encoding="utf-8")
        for name in PACKS:
            self.assertIn(f"(references/{name})", body)


if __name__ == "__main__":
    unittest.main()
