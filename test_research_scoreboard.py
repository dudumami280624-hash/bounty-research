import unittest
from research_scoreboard import scoreboard

class ScoreboardTests(unittest.TestCase):
    def test_rpc_block_is_not_source_verification(self):
        x=scoreboard({"execution":"error","error_stage":"deployment_snapshot"},None,None)
        self.assertEqual(x["real_chain_validation"],"blocked")
        self.assertEqual(x["deployment_source_correspondence"],"unverified")
        self.assertEqual(x["verified_vulnerability"],"unverified")

    def test_seven_fork_tests_without_source_match_not_promoted(self):
        x=scoreboard({"execution":"passed","tests_passed":7,"deployment_source_match_verified":False},{}, {})
        self.assertEqual(x["real_chain_validation"],"behavior_observed_source_unverified")
        self.assertEqual(x["real_chain_tests_passed"],7)
        self.assertEqual(x["official_bounty_payment"],"unverified")

    def test_verified_source_and_full_fork_tests_pass(self):
        x=scoreboard({"execution":"passed","tests_passed":7,"deployment_source_match_verified":True},None,None)
        self.assertEqual(x["real_chain_validation"],"passed")
        self.assertEqual(x["deployment_source_correspondence"],"verified")
        self.assertEqual(x["verified_vulnerability"],"unverified")

    def test_partial_tests_cannot_pass_even_with_source_match(self):
        x=scoreboard({"execution":"passed","tests_passed":6,"deployment_source_match_verified":True},None,None)
        self.assertEqual(x["real_chain_validation"],"unverified")

    def test_string_true_cannot_fake_source_verification(self):
        x=scoreboard({"execution":"passed","tests_passed":7,"deployment_source_match_verified":"true"},None,None)
        self.assertEqual(x["real_chain_validation"],"behavior_observed_source_unverified")

if __name__=="__main__": unittest.main()
