import unittest
from datetime import datetime,timezone,timedelta
from eligibility_gate import policy
class EligibilityTests(unittest.TestCase):
 def test_unverified_candidates_never_authorize_testing(self):
  a=policy({"candidates":[{"name":"fixture","open_and_authorized_verified":False,"cash_payment_verified":False}]},{"candidates":[{"name":"fixture"}]},{"findings":[{"priority":"review"}]},{"specific_pocs_executed":0})
  self.assertEqual(a["officially_verified_targets"],0)
  self.assertEqual(a["ready_for_live_testing"],0)
  self.assertFalse(a["gates"]["eligible_for_submission"])
  self.assertEqual(a["confirmed_payouts_usd"],0)
 def test_fresh_official_verification_counts_one_not_live_attack_authorization(self):
  check={"verified_at_utc":datetime.now(timezone.utc).isoformat(),
         "verified_count":1,"status":"verified",
         "scope_url":"https://immunefi.com/bug-bounty/horizen/scope/",
         "pinned_commit":"ab92502e9da98784dfe3bd3ef933d4e9345ff628"}
  r=policy({}, {}, {}, {}, scope_status=check)
  self.assertEqual(r["officially_verified_targets"],1)
  self.assertEqual(r["ready_for_live_testing"],0)
  self.assertEqual(r["confirmed_payouts_usd"],0)
 def test_stale_or_unverified_official_scope_fails_closed(self):
  check={"verified_at_utc":(datetime.now(timezone.utc)-timedelta(days=2)).isoformat(),
         "verified_count":1,"status":"verified",
         "scope_url":"https://immunefi.com/bug-bounty/horizen/scope/",
         "pinned_commit":"ab92502e9da98784dfe3bd3ef933d4e9345ff628"}
  self.assertEqual(policy({}, {}, {}, {}, scope_status=check)["officially_verified_targets"],0)
  check["verified_at_utc"]=datetime.now(timezone.utc).isoformat()
  check["status"]="unverified"
  self.assertEqual(policy({}, {}, {}, {}, scope_status=check)["officially_verified_targets"],0)
if __name__=="__main__":unittest.main()
