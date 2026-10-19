from __future__ import annotations

import unittest

from scripts.release_baseline import (
    ReleaseBaselineError,
    evaluate_baseline,
    find_baseline,
)


class FindBaselineTests(unittest.TestCase):
    def test_finds_the_highest_version_tag(self) -> None:
        self.assertEqual("v0.5.0", find_baseline(["v0.1.0", "v0.5.0", "v0.4.0"]))

    def test_orders_numerically_rather_than_lexically(self) -> None:
        self.assertEqual("v0.10.0", find_baseline(["v0.9.0", "v0.10.0"]))

    def test_ignores_tags_that_are_not_versions(self) -> None:
        self.assertEqual(
            "v0.1.0", find_baseline(["nightly", "release-candidate", "v0.1.0"])
        )

    def test_ignores_a_prerelease_or_suffixed_tag(self) -> None:
        self.assertIsNone(find_baseline(["v1.0.0-rc1", "v1.0.0+build"]))

    def test_returns_none_without_any_version_tag(self) -> None:
        self.assertIsNone(find_baseline([]))
        self.assertIsNone(find_baseline(["main", "v1", "1.0.0"]))


class EvaluateBaselineTests(unittest.TestCase):
    """ABK R14-F7 - an absent new tag must be explained, not assumed benign."""

    def test_a_real_release_passes_regardless_of_history(self) -> None:
        report = evaluate_baseline([], new_tag="v0.1.0")

        self.assertTrue(report.released)
        self.assertIn("Releasing v0.1.0", report.reason)

    def test_a_no_bump_with_a_baseline_is_a_legitimate_no_op(self) -> None:
        report = evaluate_baseline(["v0.4.0", "v0.5.0"], new_tag="")

        self.assertFalse(report.released)
        self.assertEqual("v0.5.0", report.baseline)
        self.assertIn("nothing to publish", report.reason)

    def test_a_no_bump_without_a_baseline_fails(self) -> None:
        with self.assertRaises(ReleaseBaselineError) as raised:
            evaluate_baseline([], new_tag="")

        self.assertIn("No release baseline exists", str(raised.exception))

    def test_the_failure_explains_how_to_create_the_baseline(self) -> None:
        with self.assertRaises(ReleaseBaselineError) as raised:
            evaluate_baseline(["nightly"], new_tag="")

        message = str(raised.exception)
        self.assertIn("git tag", message)
        self.assertIn("never creates a tag", message)

    def test_a_none_new_tag_is_treated_as_a_no_bump(self) -> None:
        with self.assertRaises(ReleaseBaselineError):
            evaluate_baseline([], new_tag=None)

    def test_non_version_tags_do_not_count_as_a_baseline(self) -> None:
        with self.assertRaises(ReleaseBaselineError):
            evaluate_baseline(["v1", "1.0.0", "latest"], new_tag="")


class ReleaseWorkflowTests(unittest.TestCase):
    """The caller keeps a read-only guard on every no-bump run."""

    def setUp(self) -> None:
        from pathlib import Path

        workflow = Path(__file__).resolve().parents[1] / ".github" / "workflows" / "release.yml"
        text = workflow.read_text(encoding="utf-8")
        start = text.index("\n  baseline-guard:\n")
        end = text.index("\n  preflight:\n", start)
        self.text = text
        self.guard = text[start:end]

    def test_guard_runs_exactly_when_nothing_was_computed(self) -> None:
        self.assertIn("needs: compute-version", self.guard)
        self.assertIn("if: ${{ needs.compute-version.outputs.new-tag == '' }}", self.guard)
        self.assertIn("if: ${{ needs.compute-version.outputs.new-tag != '' }}", self.text)

    def test_guard_is_read_only_and_never_tags(self) -> None:
        self.assertIn("contents: read", self.guard)
        self.assertNotIn("contents: write", self.guard)
        self.assertNotIn("git tag", self.guard)
        self.assertNotIn("git push", self.guard)

    def test_guard_sees_every_tag(self) -> None:
        self.assertIn("fetch-depth: 0", self.guard)
        self.assertIn("python scripts/release_baseline.py --new-tag ''", self.guard)

    def test_shared_workflows_are_pinned_to_one_commit(self) -> None:
        import re

        pins = set(re.findall(r"aegolius-labs/\.github/\.github/workflows/[\w-]+\.yml@([0-9a-f]+)", self.text))
        self.assertEqual(len(pins), 1, pins)
        (pin,) = pins
        self.assertEqual(len(pin), 40)
        self.assertIn(f"automation-sha: {pin}", self.text)

if __name__ == "__main__":
    unittest.main()
