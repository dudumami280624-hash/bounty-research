"""Tests for honest, bounded learning-loop evidence."""
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from student_revision_loop import revise

class RevisionLoopTests(unittest.TestCase):
    def test_feedback_can_improve_coverage_without_claiming_independence(self):
        with tempfile.TemporaryDirectory() as d:
            model=Path(d)/"fixture.gguf";model.write_bytes(b"mock only")
            replies=iter(["这个函数有问题。","缺少权限检查。应只允许授权的角色更改所有者。"])
            def runner(*args,**kwargs):
                return SimpleNamespace(returncode=0,stdout=next(replies),stderr="")
            x=revise("access-control-01",model,Path(d)/"record.json",runner=runner)
            self.assertEqual(len(x["attempts"]),2)
            self.assertTrue(x["improved_keyword_coverage"])
            self.assertFalse(x["independent_completion_verified"])
            self.assertFalse(x["agent"]["unknown_vulnerability_discovered"])
    def test_no_false_success_on_model_failure(self):
        with tempfile.TemporaryDirectory() as d:
            model=Path(d)/"fixture.gguf";model.write_bytes(b"mock only")
            def runner(*args,**kwargs):
                return SimpleNamespace(returncode=1,stdout="",stderr="failure")
            with self.assertRaises(RuntimeError):
                revise("access-control-01",model,Path(d)/"record.json",runner=runner)
if __name__=="__main__": unittest.main()
