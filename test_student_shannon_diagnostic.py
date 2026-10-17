"""Regression checks for blind Shannon diagnostic. No model download needed."""
import subprocess
import tempfile
import unittest
from pathlib import Path
from student_shannon_diagnostic import CASE, evaluate, run

class TestShannonDiagnostic(unittest.TestCase):
    def test_keyword_rubric_does_not_grant_independent_completion(self):
        self.assertEqual(sum(evaluate("没有有效诊断").values()), 0)

    def test_echoed_question_is_not_an_answer(self):
        with tempfile.TemporaryDirectory() as d:
            model=Path(d)/"dummy.gguf"
            model.touch()
            def fake(*args, **kwargs):
                return subprocess.CompletedProcess(args[0], 0, CASE, "")
            with self.assertRaisesRegex(RuntimeError, "no independent answer"):
                run(model, Path(d)/"evidence.json", runner=fake)

    def test_answer_is_saved_without_prompt(self):
        with tempfile.TemporaryDirectory() as d:
            model=Path(d)/"dummy.gguf"
            model.touch()
            response="第一次 Recon 阶段失败，根因未知；第二次 Preflight 阶段失败，Codex 额度耗尽。"
            def fake(*args, **kwargs):
                return subprocess.CompletedProcess(args[0], 0, CASE+"\n"+response, "")
            result=run(model, Path(d)/"evidence.json", runner=fake)
            self.assertEqual(result["answer"], response)
            self.assertFalse(result["independent_completion_verified"])
            self.assertTrue((Path(d)/"evidence.json").exists())

if __name__ == "__main__":
    unittest.main()
