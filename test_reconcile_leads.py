import unittest
from reconcile_leads import reconcile
class TestReconcile(unittest.TestCase):
 def test_conditional_poc_does_not_verify_real_bug(self):
  lead={"id":"a","priority":"review","check":"reentrancy-no-eth","scope_relevance":"direct_in_scope_source","description":"Reentrancy in RewardAccumulator.sendRewardsToStaker() (src/RewardAccumulator.sol#104-123)"}
  out=reconcile({"findings":[lead]},{"execution":"passed"})
  self.assertEqual(out["related_sandbox_test_leads"],1)
  self.assertEqual(out["finding_specific_pocs_executed"],0)
  self.assertEqual(out["verified_vulnerabilities"],0)
  self.assertFalse(out["cases"][0]["ready_to_submit"])
 def test_zen_staker_does_not_inherit_reward_accumulator_poc(self):
  lead={"id":"zen","priority":"review","check":"reentrancy-no-eth","scope_relevance":"direct_in_scope_source","description":"Reentrancy in ZenStaker._fetchOrDeploySurrogate(address) (src/ZenStaker.sol#50-60)"}
  out=reconcile({"findings":[lead]},{"execution":"passed"})
  self.assertEqual(out["related_sandbox_test_leads"],0)
  self.assertEqual(out["cases"][0]["poc_status"],"not_executed")
 def test_arithmetic_evidence_must_match_pinned_six_test_run(self):
  lead={"id":"12ec614578dc","priority":"review","check":"divide-before-multiply","scope_relevance":"direct_in_scope_source","description":"src/RewardAccumulator.sol#119"}
  proof={"execution":"passed","tests_passed":6,"named_tests_confirmed":True,"source_commit":"ab92502e9da98784dfe3bd3ef933d4e9345ff628"}
  out=reconcile({"findings":[lead]},proof)
  self.assertEqual(out["finding_specific_pocs_executed"],1)
  self.assertEqual(out["cases"][0]["poc_status"],"finding_specific_arithmetic_property_passed")
  self.assertEqual(out["verified_vulnerabilities"],0)
  proof["named_tests_confirmed"]=False
  self.assertEqual(reconcile({"findings":[lead]},proof)["finding_specific_pocs_executed"],0)
 def test_other_cases_remain_unverified(self):
  out=reconcile({"findings":[{"id":"x","priority":"review","check":"divide-before-multiply","scope_relevance":"direct_in_scope_source"}]},{"execution":"passed"})
  self.assertEqual(out["cases"][0]["poc_status"],"not_executed")
if __name__=="__main__":unittest.main()
