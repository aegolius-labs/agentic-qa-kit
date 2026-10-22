"""Pin how the CI plugin validation tells accepted warnings from new ones."""

from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "validate_plugin.py"
spec = importlib.util.spec_from_file_location("validate_plugin", SCRIPT)
validate_plugin = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validate_plugin)


SAMPLE = """Validating plugin manifest: .claude-plugin/plugin.json

‼ Found 1 warning:

  > version: No version specified. Consider adding a version following semver

✔ Validation passed with warnings
"""


class ValidatePluginScriptTests(unittest.TestCase):
    def test_reads_warning_lines(self) -> None:
        self.assertEqual(
            validate_plugin.warnings_in(SAMPLE),
            ["version: No version specified. Consider adding a version following semver"],
        )

    def test_accepted_warning_passes_and_new_warning_fails(self) -> None:
        accepted = ("version: No version specified",)
        self.assertEqual(
            validate_plugin.unaccepted(
                validate_plugin.warnings_in(SAMPLE), accepted
            ),
            [],
        )
        self.assertEqual(
            validate_plugin.unaccepted(["name: something new"], accepted),
            ["name: something new"],
        )

    def test_plugin_directory_checks_are_accepted(self) -> None:
        # Claude Code 2.1.307 adds these to the plugin manifest validation.
        accepted = dict((c[0], c[2]) for c in validate_plugin.CHECKS)[
            ".claude-plugin/plugin.json"
        ]
        self.assertEqual(
            validate_plugin.unaccepted(
                [
                    ".claude-plugin/plugin.json icon: No icon (ICON_MISSING). No icon found",
                    "This folder also holds a marketplace manifest. The plugin directory",
                ],
                accepted,
            ),
            [],
        )

    def test_skills_are_validated_strictly_with_no_accepted_warnings(self) -> None:
        skills = [c for c in validate_plugin.CHECKS if c[0] == "skills"]
        self.assertEqual(skills, [("skills", True, ())])


if __name__ == "__main__":
    unittest.main()
