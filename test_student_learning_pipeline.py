import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from student_learning_pipeline import retrieve, choose_course, run_once

class LearningPipelineTests(unittest.TestCase):
    def test_retrieval_returns_hash_not_answer(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "lesson.md"
            p.write_text("reentrancy state ordering", encoding="utf-8")
            result = retrieve("reentrancy state", d)
            self.assertEqual(len(result), 1)
            self.assertIn("sha256", result[0])
            self.assertNotIn("content", result[0])

    def test_course_selection_respects_prerequisites(self):
        self.assertEqual(choose_course({"verified_courses": []})["id"], "reentrancy-01")
        self.assertEqual(choose_course({"verified_courses": ["reentrancy-01"]})["id"], "access-control-01")

    def test_persist_evidence_without_false_promotion(self):
        with tempfile.TemporaryDirectory() as d:
            root = Path(d)
            with patch("student_learning_pipeline.revise", return_value={"attempts": [{"answer": "sample"}], "improved_keyword_coverage": True}):
                with patch("student_authorization.require_authorization", return_value=None):
                    class Result:
                        returncode = 0
                        stdout = "2 tests passed"
                        stderr = ""
                    record = run_once("unused.gguf", root, root / "memory.json", root / "evidence", "reentrancy-01", forge_runner=lambda *args, **kwargs: Result())
            self.assertTrue(record["lab"]["passed"])
            self.assertFalse(record["model_independent_solution_verified"])
            self.assertFalse(record["held_out_problem_passed"])
            saved = json.loads((root / "memory.json").read_text())
            self.assertEqual(len(saved["sessions"]), 1)
            self.assertEqual(saved["verified_courses"], [])

if __name__ == "__main__":
    unittest.main()
