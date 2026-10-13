import unittest
from research_scoreboard import scoreboard

class ScoreboardTests(unittest.TestCase):
    def test_green_ci_does_not_claim_fork(self):
        x=scoreboard({"execution":"error","error_stage":"deployment_snapshot"},None,None)
        self.assertEqual(x["real_chain_validation"],"blocked")
        self.assertEqual(x["verified_vulnerability"],"unverified")
        self.assertEqual(x["official_bounty_payment"],"unverified")
    def test_seven_verified_tests_are_distinct_from_bounty(self):
        x=scoreboard({"execution":"passed","tests_passed":7},{}, {})
        self.assertEqual(x["real_chain_validation"],"passed")
        self.assertEqual(x["official_bounty_payment"],"unverified")
    def test_partial_tests_do_not_pass(self):
        x=scoreboard({"execution":"passed","tests_passed":6},None,None)
        self.assertEqual(x["real_chain_validation"],"unverified")

if __name__=="__main__":
    unittest.main()
