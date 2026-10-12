import unittest
import tempfile
from pathlib import Path
from unittest.mock import patch
from submission_gate import ready

def valid_case():
    return dict(verified=True,bounty_scope_verified=True,known_issue_checked=True,
                impact_verified=True,poc_passed=True,evidence_path="evidence/local.json",
                explicit_submission_approved=True)

class SubmissionGating(unittest.TestCase):
    def test_no_evidence_no_submission(self):
        self.assertFalse(ready({"verified":True}))
    def test_missing_file_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            with patch("submission_gate.ROOT",Path(folder)):
                self.assertFalse(ready(valid_case()))
    def test_nonempty_evidence_and_approval_required(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            (root/"evidence").mkdir()
            target=root/"evidence"/"local.json"
            with patch("submission_gate.ROOT",root):
                self.assertFalse(ready(valid_case()))
                target.write_text('{"test":"fixture"}',encoding="utf-8")
                case=valid_case()
                case["explicit_submission_approved"]=False
                self.assertFalse(ready(case))
                case["explicit_submission_approved"]=True
                self.assertTrue(ready(case))
    def test_traversal_is_rejected(self):
        case=valid_case()
        case["evidence_path"]="evidence/../bad"
        self.assertFalse(ready(case))
if __name__=="__main__":unittest.main()
