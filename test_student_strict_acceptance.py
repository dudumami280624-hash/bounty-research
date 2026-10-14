import unittest
from student_learning_acceptance import evaluate

class StrictLearningAcceptanceTests(unittest.TestCase):
    def setUp(self):
        self.revision={"revision_observed":True,"improved_keyword_coverage":True}
        self.patch={"real_model_invoked":True,"independent_patch_test_passed":True,
                    "attempts":[{"forge_passed":True,"deterministic_fixes":[]}]}
        self.unseen={"unseen_fixture":True,"model_generated_patch":True,
                     "forge_passed":True,"deterministic_fixes":[],"authorization_verified":True}
    def test_assisted_is_not_independent(self):
        p={**self.patch,"attempts":[{"forge_passed":True,"deterministic_fixes":["static repair"]}]}
        self.assertFalse(evaluate(self.revision,p,self.unseen)["autonomous_learning_accepted"])
    def test_no_held_out_evidence_is_rejected(self):
        self.assertFalse(evaluate(self.revision,self.patch)["autonomous_learning_accepted"])
    def test_unverified_scope_is_rejected(self):
        h={**self.unseen,"authorization_verified":False}
        self.assertFalse(evaluate(self.revision,self.patch,h)["autonomous_learning_accepted"])
    def test_all_independent_evidence_required(self):
        self.assertTrue(evaluate(self.revision,self.patch,self.unseen)["autonomous_learning_accepted"])
    def test_model_not_invoked_is_rejected(self):
        self.assertFalse(evaluate(self.revision,{**self.patch,"real_model_invoked":False},self.unseen)["autonomous_learning_accepted"])

if __name__=="__main__":
    unittest.main()
