import unittest
from scope_review import classify
class SourceScopeTests(unittest.TestCase):
 def test_auxiliary_notifier_excluded_only_if_exact_path(self):
  d=classify([{"id":"df03bce1714d","priority":"review","check":"arbitrary-send-erc20","description":"TransferFromRewardNotifier._sendTokensToReceiver() (src/notifiers/TransferFromRewardNotifier.sol#71-73)"}])
  self.assertEqual(d["excluded_from_direct_scope"],1)
  d=classify([{"id":"df03bce1714d","priority":"review","description":"src/RewardAccumulator.sol"}])
  self.assertEqual(d["classification_errors"],1)
 def test_direct_issue_not_marked_verified(self):
  d=classify([{"id":"8e48c2a2804a","priority":"review","check":"reentrancy-no-eth","description":"src/RewardAccumulator.sol#104-123"}])
  self.assertEqual(d["direct_requires_poc"],1)
  self.assertFalse(d["findings"][0]["verified_vulnerability"])
if __name__=="__main__":unittest.main()
