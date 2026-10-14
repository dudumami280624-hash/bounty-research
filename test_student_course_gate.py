"""Tests for course prerequisites and evidence-based progression."""
import unittest
from student_course_gate import evaluate
class CourseGateTests(unittest.TestCase):
    def test_empty_evidence_never_passes(self):
        result=evaluate({})
        self.assertTrue(result["reentrancy-01"]["unlocked"])
        self.assertFalse(result["reentrancy-01"]["passed"])
        self.assertFalse(result["access-control-01"]["unlocked"])
    def test_model_answer_alone_does_not_pass(self):
        record={"reentrancy-01":{"assessment":{"independent_completion_verified":True}}}
        self.assertFalse(evaluate(record)["reentrancy-01"]["passed"])
    def test_verified_first_course_unlocks_next_but_not_passes(self):
        record={"reentrancy-01":{"assessment":{"independent_completion_verified":True,"held_out_verified":True},
          "lab":{"executed":True,"passed":True},"human_review_approved":True}}
        result=evaluate(record)
        self.assertTrue(result["reentrancy-01"]["passed"])
        self.assertTrue(result["access-control-01"]["unlocked"])
        self.assertFalse(result["access-control-01"]["passed"])
        self.assertFalse(result["arithmetic-01"]["unlocked"])
if __name__=="__main__":unittest.main()
