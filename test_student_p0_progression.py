import json
import tempfile
import unittest
from pathlib import Path
from student_p0_progression import evaluate, write_result


def fixture(lesson, n):
    return {
        "engine": "upstream-aider-cli", "lesson": lesson,
        "model": "openai/local-coder", "endpoint_loopback": True,
        "reference_excluded_from_agent_workspace": True,
        "real_model_invoked": True, "model_generated_patch": True,
        "forge_passed": True, "unseen_fixture": lesson.startswith("held-out"),
        "authorization_verified": True, "deterministic_fixes": [],
        "attempts": [{"edit_applied": True, "forge_executed": True,
                      "forge_exit_code": 0, "forge_passed": True,
                      "passing_tests": n, "deterministic_fixes": []}],
    }


class LocalProgressionTests(unittest.TestCase):
    def setUp(self):
        self.training = fixture("reentrancy-01", 2)
        self.unseen = fixture("held-out-access-control-01", 5)

    def test_training_and_genuine_unseen_required(self):
        result = evaluate(self.training, self.unseen)
        self.assertTrue(result["local_training_progression_approved"])
        self.assertEqual(result["unlocked_next_lesson"], "access-control-01")
        self.assertFalse(result["formal_course_graduated"])

    def test_empty_evidence_rejected(self):
        self.assertFalse(evaluate({}, {})["local_training_progression_approved"])

    def test_hidden_test_count_required(self):
        self.unseen["attempts"][0]["passing_tests"] = 0
        self.assertFalse(evaluate(self.training, self.unseen)["local_training_progression_approved"])

    def test_assisted_fixes_rejected(self):
        self.unseen["attempts"][0]["deterministic_fixes"] = ["manual replacement"]
        self.assertFalse(evaluate(self.training, self.unseen)["local_training_progression_approved"])

    def test_remote_or_mismatched_model_rejected(self):
        self.unseen["endpoint_loopback"] = False
        self.assertFalse(evaluate(self.training, self.unseen)["local_training_progression_approved"])
        self.unseen["endpoint_loopback"] = True
        self.unseen["model"] = "openai/other-model"
        self.assertFalse(evaluate(self.training, self.unseen)["local_training_progression_approved"])

    def test_failed_assessment_does_not_write_verified_memory(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            train, hold, out, memory = [root / x for x in ("training.json", "held-out.json", "result.json", "memory.json")]
            train.write_text(json.dumps(self.training))
            self.unseen["attempts"][0]["forge_passed"] = False
            hold.write_text(json.dumps(self.unseen))
            write_result(train, hold, out, memory)
            self.assertFalse(memory.exists())


if __name__ == "__main__":
    unittest.main()
