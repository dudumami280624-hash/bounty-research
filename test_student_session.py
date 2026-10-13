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
    def test_knowledge_matches_curated_lesson_without_awarding_completion(self):
        with tempfile.TemporaryDirectory() as tmp:
            index=Path(tmp)/"index.json"
            index.write_text(json.dumps({"curated:one":{"source":"curated-case","title":"Reentrancy lesson","category":"reentrancy","invariant":"balance conserved","verification":"unverified"},"ghsa:two":{"source":"github-reviewed-advisory","title":"Reentrancy"}}))
            def fake_forge(command,**kwargs):
                return SimpleNamespace(returncode=0,stdout="passed",stderr="")
            result=run_session("fixed-seed",{},Path(tmp)/"record.json",runner=fake_forge,knowledge_index=index)
            self.assertEqual(result["knowledge"]["status"],"matched")
            self.assertEqual(len(result["knowledge"]["entries"]),1)
            self.assertFalse(result["completed"])
    def test_missing_knowledge_cannot_fabricate_a_match(self):
        with tempfile.TemporaryDirectory() as tmp:
            result=run_session("fixed-seed",{},Path(tmp)/"record.json",runner=lambda *a,**k: SimpleNamespace(returncode=0,stdout="",stderr=""),knowledge_index=Path(tmp)/"absent.json")
            self.assertEqual(result["knowledge"]["status"],"missing")
            self.assertFalse(result["completed"])
if __name__=="__main__":
    unittest.main()
