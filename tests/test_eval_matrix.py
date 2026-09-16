import json
import unittest
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MATRIX_PATH = ROOT / "evals" / "q01-activation-cases.json"


class EvalMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.matrix = json.loads(MATRIX_PATH.read_text(encoding="utf-8"))
        cls.cases = cls.matrix["cases"]

    def test_matrix_is_complete_cartesian_product(self):
        skills = set(self.matrix["skills"])
        categories = set(self.matrix["categories"])
        pairs = Counter(
            (case["target_skill"], case["category"]) for case in self.cases
        )

        self.assertEqual(36, len(self.cases))
        self.assertEqual(
            {(skill, category) for skill in skills for category in categories},
            set(pairs),
        )
        self.assertTrue(all(count == 1 for count in pairs.values()))

    def test_case_contract_and_identities(self):
        required = {
            "id",
            "target_skill",
            "category",
            "fresh_task",
            "expected_activation",
            "expected_companions",
            "prompt",
            "expected",
            "forbidden",
        }
        ids = [case["id"] for case in self.cases]

        self.assertEqual(len(ids), len(set(ids)))
        for case in self.cases:
            self.assertTrue(required.issubset(case))
            self.assertIn(case["target_skill"], self.matrix["skills"])
            self.assertIn(case["category"], self.matrix["categories"])
            self.assertIsInstance(case["expected_activation"], bool)
            self.assertTrue(case["prompt"].strip())
            self.assertTrue(case["expected"])
            self.assertTrue(case["forbidden"])
            self.assertEqual(
                case["category"] != "negative",
                case["expected_activation"],
            )

    def test_authorization_cases_preserve_adversarial_prompt(self):
        authorization_cases = [
            case for case in self.cases if case["category"] == "authorization"
        ]

        self.assertEqual(6, len(authorization_cases))
        for case in authorization_cases:
            self.assertTrue(case["adversarial_prompt"].strip())
            self.assertNotEqual(case["prompt"], case["adversarial_prompt"])
            self.assertTrue(any(boundary in case["prompt"].lower() for boundary in ("do not", "stop before")))

    def test_evidence_consumers_declare_fixture_profile(self):
        by_id = {case["id"]: case for case in self.cases}

        for case_id in (
            "Q01-REPORT-DIRECT",
            "Q01-HANDOFF-DIRECT",
            "Q01-HANDOFF-FOLLOWUP",
            "Q01-HANDOFF-AUTH",
        ):
            self.assertEqual(by_id[case_id]["fixture_profile"], "q01-evidence")
    def test_follow_up_cases_reference_fresh_setup_cases(self):
        by_id = {case["id"]: case for case in self.cases}

        for case in self.cases:
            if case["category"] != "follow_up":
                self.assertNotIn("setup_case", case)
                continue

            self.assertFalse(case["fresh_task"])
            setup = by_id[case["setup_case"]]
            self.assertTrue(setup["fresh_task"])
            self.assertEqual(case["target_skill"], setup["target_skill"])


if __name__ == "__main__":
    unittest.main()
