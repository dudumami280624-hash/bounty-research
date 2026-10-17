"""Regression checks for blind Shannon diagnosis; no model download needed."""
import subprocess,tempfile,unittest
from pathlib import Path
from student_shannon_diagnostic import CASE,evaluate,run

GOOD=("A: recon 后 agent 执行失败，根因未知。B: 在 preflight 预检阶段失败，直接 Pi 请求显示额度限制，"
      "这解释 B 但不能据此断言 A 同因。保存脱敏日志并用最小请求诊断。")
class TestShannonDiagnostic(unittest.TestCase):
    def test_bad_answer_fails_rubric(self):
        self.assertFalse(all(evaluate("继续重跑。")))

    def test_echoed_prompt_is_not_answer(self):
        with tempfile.TemporaryDirectory() as d:
            model=Path(d)/"dummy.gguf";model.touch()
            def fake(*args,**kwargs): return subprocess.CompletedProcess(args[0],0,CASE,"")
            with self.assertRaises(RuntimeError): run(model,Path(d)/"evidence.json",runner=fake)

    def test_answer_and_failure_status_saved(self):
        with tempfile.TemporaryDirectory() as d:
            model=Path(d)/"dummy.gguf";model.touch()
            def fake(*args,**kwargs): return subprocess.CompletedProcess(args[0],0,GOOD,"")
            result=run(model,Path(d)/"evidence.json",runner=fake)
            self.assertEqual(result["answer"],GOOD)
            self.assertTrue(result["rubric_passed"])
            self.assertFalse(result["independent_completion_verified"])
            self.assertTrue((Path(d)/"evidence.json").exists())

if __name__=="__main__": unittest.main()
