import unittest
from scope_review import classify

class SourceScopeTests(unittest.TestCase):
 def test_auxiliary_excluded_based_on_source_not_identifier(self):
  item={"id":"new-random-id","priority":"review","check":"arbitrary-send-erc20",
        "locations":[{"path":"src/notifiers/TransferFromRewardNotifier.sol"}]}
  self.assertEqual(classify([item])["excluded_from_direct_scope"],1)

 def test_slither_mapped_paths_override_misleading_prose(self):
  item={"id":"any-id","priority":"review","check":"reentrancy-no-eth",
        "description":"Mention of src/ZenStaker.sol but actual location differs",
        "locations":[{"path":"src/notifiers/TransferRewardNotifier.sol"}]}
  self.assertEqual(classify([item])["direct_requires_poc"],0)
  self.assertEqual(classify([item])["excluded_from_direct_scope"],1)

 def test_direct_issue_not_marked_verified(self):
  item={"id":"dynamic-id","priority":"review","check":"reentrancy-no-eth",
        "locations":[{"path":"src/RewardAccumulator.sol"}]}
  result=classify([item])
  self.assertEqual(result["direct_requires_poc"],1)
  self.assertFalse(result["findings"][0]["verified_vulnerability"])

 def test_unknown_sources_fail_closed_without_blocking_pipeline(self):
  item={"id":"brand-new","priority":"review","check":"unknown",
        "locations":[{"path":"src/NewContract.sol"}]}
  result=classify([item])
  self.assertEqual(result["scope_not_established"],1)
  self.assertEqual(result["total_leads"],1)
  self.assertEqual(result["verified_vulnerabilities"],0)

if __name__=="__main__":unittest.main()
