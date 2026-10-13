import unittest
from student_progress import assess

class ProgressTests(unittest.TestCase):
    def test_empty_cannot_pass(self):
        self.assertEqual(assess({})["status"],"incomplete")
    def test_keyword_only_cannot_pass(self):
        self.assertFalse(assess({"lesson":"a","exercise":"b"})["verified"])
    def test_assisted_cannot_pass(self):
        row={k:"evidence" for k in ("lesson","exercise","reproduction","repair","regression","explanation")}
        row.update(independent=False,reviewer_approved=True)
        self.assertEqual(assess(row)["status"],"assisted_or_unknown")
    def test_unreviewed_cannot_pass(self):
        row={k:"evidence" for k in ("lesson","exercise","reproduction","repair","regression","explanation")}
        row.update(independent=True)
        self.assertEqual(assess(row)["status"],"awaiting_review")
if __name__=="__main__":
    unittest.main()
