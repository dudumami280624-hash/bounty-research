import unittest
from propose_repair import proposal

class RepairPlannerTests(unittest.TestCase):
    def test_rpc_outage_never_claims_repair(self):
        p=proposal({"status":"rpc_blocked"})
        self.assertEqual(p["kind"],"rpc_provider_required")
        self.assertFalse(p["safe_to_merge"])
    def test_healthy_never_modifies_code(self):
        self.assertIsNone(proposal({"status":"healthy"})["change"])
    def test_unknown_never_auto_merges(self):
        self.assertFalse(proposal({"status":"unexpected"})["safe_to_merge"])

if __name__=="__main__":
    unittest.main()
