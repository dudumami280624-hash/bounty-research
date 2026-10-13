import json
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from student_session import run_session

class SessionTests(unittest.TestCase):
    def test_complete_pipeline_records_but_does_not_fake_student_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            out=Path(tmp)/"record.json"
            def fake_forge(command,**kwargs):
                self.assertEqual(command[:3],["forge","test","--root"])
                return SimpleNamespace(returncode=0,stdout="2 tests passed",stderr="")
            result=run_session("fixed-seed",{},out,runner=fake_forge)
            self.assertTrue(result["forge"]["passed"])
            self.assertFalse(result["completed"])
            self.assertEqual(json.loads(out.read_text())["assessment"]["status"],"incomplete")
            self.assertIn("feedback",result)
    def test_failed_forge_cannot_complete(self):
        with tempfile.TemporaryDirectory() as tmp:
            def fake_forge(command,**kwargs):
                return SimpleNamespace(returncode=1,stdout="failed",stderr="")
            evidence={k:"proof" for k in ("lesson","exercise","reproduction","repair","regression","explanation")}
            evidence.update(independent=True,reviewer_approved=True)
            result=run_session("fixed-seed",evidence,Path(tmp)/"record.json",runner=fake_forge)
            self.assertFalse(result["completed"])
            self.assertFalse(result["forge"]["passed"])
if __name__=="__main__":
    unittest.main()
