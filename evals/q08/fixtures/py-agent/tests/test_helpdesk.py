import json
import os
import tempfile
import unittest
from pathlib import Path

from helpdesk import agent

TASK = json.loads((Path(__file__).resolve().parents[1] / "tasks" / "refund-1042.json").read_text(encoding="utf-8"))


class AgentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.cwd = os.getcwd()
        self.tmp = tempfile.TemporaryDirectory()
        os.chdir(self.tmp.name)
        agent.reset()

    def tearDown(self) -> None:
        os.chdir(self.cwd)
        self.tmp.cleanup()

    def test_refund_is_issued_and_the_customer_is_emailed(self) -> None:
        summary = agent.run(TASK, seed=0)
        self.assertIn("has been issued", summary["reply"])
        orders = json.loads(Path(".sandbox/orders.json").read_text(encoding="utf-8"))
        self.assertTrue(orders["1042"]["refunded"])
        outbox = Path(".sandbox/outbox.jsonl").read_text(encoding="utf-8")
        self.assertIn("ana.lima@customers.example", outbox)

    def test_the_same_seed_gives_the_same_run(self) -> None:
        first = agent.run(TASK, seed=2)
        agent.reset()
        self.assertEqual(first, agent.run(TASK, seed=2))

    def test_an_operator_stop_ends_the_ticket(self) -> None:
        summary = agent.run(TASK, seed=0, stop_after=1)
        self.assertIn("handed back", summary["reply"])
        self.assertEqual(1, summary["tool_calls"])

    def test_large_refunds_go_to_a_person(self) -> None:
        task = dict(TASK, ticket="T-882", order_id="1043")
        summary = agent.run(task, seed=0)
        self.assertIn("passed to a member of our team", summary["reply"])
        orders = json.loads(Path(".sandbox/orders.json").read_text(encoding="utf-8"))
        self.assertFalse(orders["1043"]["refunded"])

    def test_an_email_timeout_is_retried(self) -> None:
        summary = agent.run(TASK, seed=0, fault="email-timeout")
        self.assertNotIn("could not email", summary["reply"])


if __name__ == "__main__":
    unittest.main()
