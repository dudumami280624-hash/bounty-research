import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from student_learning_pipeline import run_once

class TwoSessionMemoryTests(unittest.TestCase):
    def test_real_context_is_forwarded_across_two_sessions(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            knowledge=root/"knowledge"
            knowledge.mkdir()
            (knowledge/"reentrancy.md").write_text("提款 状态 外部调用 先更新状态再调用",encoding="utf-8")
            contexts=[]
            def fake_revision(lesson,model,output,learning_context=""):
                contexts.append(learning_context)
                return {"attempts":[{"feedback":{"missing":["状态","外部调用"]}}],
                        "improved_keyword_coverage":False}
            class FakeForge:
                returncode=1
                stdout="failed teaching test"
                stderr=""
            with patch("student_learning_pipeline.revise",side_effect=fake_revision):
                with patch("student_learning_pipeline.require_authorization"):
                    for _ in range(2):
                        run_once("fake-model",knowledge,root/"memory.json",root/"evidence",
                                 "reentrancy-01",forge_runner=lambda *args,**kwargs:FakeForge())
            self.assertEqual(len(contexts),2)
            self.assertIn("先更新状态",contexts[0])
            self.assertIn("Previous gap",contexts[1])
            self.assertIn("failed teaching test",contexts[1])
            records=json.loads((root/"memory.json").read_text())
            self.assertEqual(len(records["sessions"]),2)
            self.assertEqual(records["verified_courses"],[])
            self.assertFalse(records["sessions"][1]["lab"]["passed"])
            self.assertTrue(records["sessions"][1]["prior_failure_context_sent"])

if __name__=="__main__":
    unittest.main()
