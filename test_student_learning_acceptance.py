import unittest
from student_learning_acceptance import evaluate

class LearningAcceptanceTests(unittest.TestCase):
    def test_assisted_pass_not_autonomous(self):
        result = evaluate(
            {"revision_observed": True, "improved_keyword_coverage": True, "attempts": [{}, {}]},
            {"real_model_invoked": True, "independent_patch_test_passed": True,
             "attempts": [{"forge_passed": True, "deterministic_fixes": ["move balance reset"]}]})
        self.assertTrue(result["assisted_foundry_passed"])
        self.assertFalse(result["autonomous_learning_accepted"])
    def test_model_only_with_improvement_accepted(self):
        result = evaluate(
            {"revision_observed": True, "improved_keyword_coverage": True, "attempts": [{}, {}]},
            {"real_model_invoked": True, "independent_patch_test_passed": True,
             "attempts": [{"forge_passed": True, "deterministic_fixes": []}]})
        self.assertTrue(result["autonomous_learning_accepted"])
    def test_no_improvement_not_accepted(self):
        result = evaluate(
            {"revision_observed": True, "improved_keyword_coverage": False},
            {"real_model_invoked": True, "independent_patch_test_passed": True,
             "attempts": [{"forge_passed": True, "deterministic_fixes": []}]})
        self.assertFalse(result["autonomous_learning_accepted"])
if __name__ == "__main__": unittest.main()
