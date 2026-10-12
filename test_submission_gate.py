import unittest
from submission_gate import ready
class SubmissionGating(unittest.TestCase):
 def test_no_evidence_no_submission(self):
  self.assertFalse(ready({"verified":True}))
 def test_needs_explicit_approval(self):
  case=dict(verified=True,bounty_scope_verified=True,known_issue_checked=True,impact_verified=True,poc_passed=True,evidence_path="evidence/local.json",explicit_submission_approved=False)
  self.assertFalse(ready(case))
  case["explicit_submission_approved"]=True
  self.assertTrue(ready(case))
 def test_traversal_is_rejected(self):
  case=dict(verified=True,bounty_scope_verified=True,known_issue_checked=True,impact_verified=True,poc_passed=True,evidence_path="evidence/../bad",explicit_submission_approved=True)
  self.assertFalse(ready(case))
if __name__=="__main__":unittest.main()
