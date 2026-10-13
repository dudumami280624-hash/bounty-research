"""Learning-track configuration guard: keep training evidence separate from bounty submissions."""
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parent

class LearningTrackTests(unittest.TestCase):
    def test_learning_path_exists_with_all_stages(self):
        text=(ROOT/"LEARNING_PATH_ZH.md").read_text(encoding="utf-8")
        for term in ("重入漏洞","访问控制","整数精度","修复前可复现","盲测","不等于学生独立完成"):
            self.assertIn(term,text)

    def test_knowledge_collection_is_scheduled_twice_daily(self):
        workflow=(ROOT/".github/workflows/monthly-knowledge.yml").read_text()
        self.assertIn("20 3,15 * * *",workflow)

    def test_blind_lab_is_explicitly_labeled_scanner_not_student(self):
        text=(ROOT/"LEARNING_PATH_ZH.md").read_text()
        self.assertIn("真实扫描器的样本识别评估",text)
        self.assertIn("不等于学生独立完成",text)

if __name__=="__main__":
    unittest.main()
