import json
import tempfile
import unittest
from pathlib import Path
from student_autonomous import run_autonomous_baseline

class AutonomousBaselineTests(unittest.TestCase):
    def test_baseline_practices_and_records_correction_without_claiming_discovery(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/"autonomous.json"
            record=run_autonomous_baseline("reentrancy-01",out)
            self.assertEqual(len(record["attempts"]),2)
            self.assertTrue(record["revision_observed"])
            self.assertTrue(record["improved_keyword_coverage"])
            self.assertFalse(record["independent_completion_verified"])
            self.assertFalse(record["agent"]["model_inference_executed"])
            self.assertEqual(json.loads(out.read_text())["agent"]["type"],"deterministic_curated_baseline")
    def test_unsupported_lesson_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(ValueError):
                run_autonomous_baseline("unknown",Path(d)/"out.json")
if __name__=="__main__":
    unittest.main()
