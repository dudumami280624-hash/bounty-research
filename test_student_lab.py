import unittest
from student_lab import LESSONS,grade
class StudentLabTests(unittest.TestCase):
    def test_lessons(self):
        self.assertGreaterEqual(len(LESSONS),2)
    def test_blank_not_pass(self):
        self.assertEqual(grade("reentrancy-01","")["status"],"incomplete")
    def test_keyword_match_not_pass(self):
        result=grade("reentrancy-01","先状态更新再外部调用")
        self.assertEqual(result["status"],"review_required")
        self.assertTrue(result["human_review_required"])
    def test_unknown_lesson(self):
        with self.assertRaises(ValueError):
            grade("not-real","hello")
if __name__=="__main__":
    unittest.main()
