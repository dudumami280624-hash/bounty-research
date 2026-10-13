import json
import tempfile
import unittest
from pathlib import Path
from student_practice import practice

class PracticeTests(unittest.TestCase):
    def test_revision_records_real_attempts_but_not_independence(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"practice.json"
            r=practice("reentrancy-01",["不知道","先更新状态，再执行外部调用"],p)
            self.assertEqual(len(r["attempts"]),2)
            self.assertTrue(r["improved_keyword_coverage"])
            self.assertFalse(r["independent_completion_verified"])
            self.assertEqual(json.loads(p.read_text())["attempts"][0]["answer"],"不知道")
    def test_empty_attempts_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                practice("reentrancy-01",[],Path(d)/"record.json")
if __name__=="__main__":
    unittest.main()
