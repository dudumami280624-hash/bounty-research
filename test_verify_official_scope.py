import unittest
from verify_official_scope import validate_pages, EXPECTED_INFO, EXPECTED_SCOPE, PINNED_SHA

class OfficialScopeTests(unittest.TestCase):
 def setUp(self):
  self.evidence={
   "information_url":EXPECTED_INFO,"scope_url":EXPECTED_SCOPE,
   "pinned_commit":PINNED_SHA,
   "direct_source_assets":["src/ZenStaker.sol","src/RewardAccumulator.sol"]}
  self.information="Horizen Maximum Bounty $10,000 Submit a Bug Runnable PoC Required Rewards in USDC"
  self.scope="Horizen Assets in Scope ZenStaker RewardAccumulator ab92502 Submit a Bug"
 def test_official_pages_with_assets_bounty_and_submit(self):
  verified,_=validate_pages(self.evidence,self.information,self.scope)
  self.assertTrue(verified)
 def test_directory_cannot_authorize_without_official_html(self):
  verified,_=validate_pages(self.evidence,"Third party lists horizen",self.scope)
  self.assertFalse(verified)
 def test_without_asset_commit_or_submit_fails(self):
  for wrong in ("Horizen Assets in Scope ZenStaker RewardAccumulator Submit a Bug",
                "Horizen Assets in Scope ZenStaker ab92502 Submit a Bug",
                "Horizen Assets in Scope ZenStaker RewardAccumulator ab92502"):
   self.assertFalse(validate_pages(self.evidence,self.information,wrong)[0])
 def test_scope_url_or_pinned_sha_cannot_be_modified(self):
  for key,value in (("scope_url","https://phish.example/scope"),("pinned_commit","test")):
   original=self.evidence[key]
   self.evidence[key]=value
   self.assertFalse(validate_pages(self.evidence,self.information,self.scope)[0])
   self.evidence[key]=original
if __name__=="__main__":unittest.main()
