import json
import unittest
from unittest.mock import patch

from fleet_next import commander


class CommanderTests(unittest.TestCase):
    def test_first_turn_sets_policy_and_uses_subscription_cli(self):
        argv = commander.command("", "show active work")
        self.assertEqual(argv[:6], ["codex", "exec", "--json",
                                    "--skip-git-repo-check", "--sandbox",
                                    "read-only"])
        self.assertIn("fresh `<fleet-context>`", commander.SYSTEM)
        self.assertIn("show active work", argv[-1])

    def test_later_turn_resumes_exact_thread(self):
        self.assertEqual(
            commander.command("thread-1", "approve"),
            ["codex", "exec", "resume", "--json", "--skip-git-repo-check",
             "thread-1", "approve"])

    @patch("fleet_next.commander.remember")
    def test_thread_identity_lives_in_tmux(self, remember):
        output = commander.event(json.dumps(
            {"type": "thread.started", "thread_id": "thread-1"}))
        self.assertEqual(output, "")
        remember.assert_called_once_with("thread-1")

    def test_agent_message_is_visible(self):
        output = commander.event(json.dumps({
            "type": "item.completed",
            "item": {"type": "agent_message", "text": "proposal"},
        }))
        self.assertEqual(output, "proposal")


if __name__ == "__main__":
    unittest.main()
