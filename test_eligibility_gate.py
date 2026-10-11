import unittest
from eligibility_gate import policy
class EligibilityTests(unittest.TestCase):
 def test_unverified_candidates_never_authorize_testing(self):
  a=policy({"candidates":[{"name":"fixture","open_and_authorized_verified":False,"cash_payment_verified":False}]},{"candidates":[{"name":"fixture"}]},{"findings":[{"priority":"review"}]},{"specific_pocs_executed":0})
  self.assertEqual(a["officially_verified_targets"],0)
  self.assertEqual(a["ready_for_live_testing"],0)
  self.assertFalse(a["gates"]["eligible_for_submission"])
  self.assertEqual(a["confirmed_payouts_usd"],0)
if __name__=="__main__":unittest.main()
