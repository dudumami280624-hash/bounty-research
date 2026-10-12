import unittest
from reconcile_leads import reconcile
class TestReconcile(unittest.TestCase):
 def test_conditional_poc_does_not_verify_real_bug(self):
  lead={"id":"a","priority":"review","check":"reentrancy-no-eth","scope_relevance":"direct_in_scope_source"}
  out=reconcile({"findings":[lead]},{"execution":"passed"})
  self.assertEqual(out["conditional_evidence_leads"],1)
  self.assertEqual(out["verified_vulnerabilities"],0)
  self.assertFalse(out["cases"][0]["ready_to_submit"])
 def test_other_cases_remain_unverified(self):
  out=reconcile({"findings":[{"id":"x","priority":"review","check":"divide-before-multiply","scope_relevance":"direct_in_scope_source"}]},{"execution":"passed"})
  self.assertEqual(out["cases"][0]["poc_status"],"not_executed")
if __name__=="__main__":unittest.main()
