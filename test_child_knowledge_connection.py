"""Offline knowledge bridge regression: no student completion is inferred."""
import json
import tempfile
import unittest
from pathlib import Path
from student_session import load_lesson_knowledge

class KnowledgeBridgeTests(unittest.TestCase):
    def test_matching_curated_lesson_is_reference_only(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"index.json"
            p.write_text(json.dumps({"curated:1":{"source":"curated-case","title":"Reentrancy","invariant":"Balances conserved","verification":"unverified"}}))
            data=load_lesson_knowledge(p,"reentrancy-01")
            self.assertEqual(data["status"],"matched")
            self.assertEqual(data["entries"][0]["verification"],"unverified")
    def test_unrelated_and_untrusted_sources_are_excluded(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"index.json"
            p.write_text(json.dumps({"ghsa:1":{"source":"github-reviewed-advisory","title":"Reentrancy"},"curated:2":{"source":"curated-case","title":"Access control","invariant":"Only owner"}}))
            data=load_lesson_knowledge(p,"reentrancy-01")
            self.assertEqual(data["status"],"no_match")
            self.assertEqual(data["entries"],[])

if __name__=="__main__":
    unittest.main()
