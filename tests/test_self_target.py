"""Keep this repository usable as a QA target of itself.

Q09 dogfoods the kit by running its own workflows against this repository. That
only works while `.agentic-qa/manifest.json` stays tracked and contract-valid. A
blanket ignore rule or a schema drift would silently remove the target, so the
condition is asserted rather than assumed.
"""

from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

from agentic_qa_kit.model import validate_manifest


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / ".agentic-qa" / "manifest.json"


class SelfTargetTests(unittest.TestCase):
    def test_self_manifest_exists_and_validates(self) -> None:
        self.assertTrue(MANIFEST.is_file(), "the Q09 self-target manifest is missing")
        validate_manifest(json.loads(MANIFEST.read_text(encoding="utf-8")))

    def test_self_manifest_is_tracked(self) -> None:
        result = subprocess.run(
            ["git", "check-ignore", str(MANIFEST)],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        # git check-ignore exits 1 when the path is not ignored, which is the
        # state this test requires. Exit 128 means git is unavailable here.
        if result.returncode == 128:
            self.skipTest("git is unavailable")
        self.assertEqual(
            result.returncode,
            1,
            "the self-target manifest is ignored; generated evidence may be ignored too broadly",
        )

    def test_generated_session_evidence_stays_ignored(self) -> None:
        candidate = ROOT / ".agentic-qa" / "sessions" / "example" / "session.json"
        result = subprocess.run(
            ["git", "check-ignore", str(candidate)],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        if result.returncode == 128:
            self.skipTest("git is unavailable")
        self.assertEqual(
            result.returncode,
            0,
            "generated session evidence must stay untracked; it can contain environment detail",
        )

    def test_self_target_ledger_validates_end_to_end(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "qa.py"), "validate", "--root", str(ROOT)],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue(json.loads(result.stdout)["valid"])

    def test_profile_covers_the_attributes_q09_claims(self) -> None:
        payload = json.loads(MANIFEST.read_text(encoding="utf-8"))
        attributes = {entry["attribute"] for entry in payload["quality_profile"]}
        # Compatibility is the attribute Q09 exists to evaluate; data-integrity
        # and security carry the ledger's critical invariants.
        for required in ("compatibility", "data-integrity", "security"):
            self.assertIn(required, attributes)


if __name__ == "__main__":
    unittest.main()
