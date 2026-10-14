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
    def test_invalid_utf8_output_is_decoded_with_replacement(self):
        with tempfile.TemporaryDirectory() as d:
            model=Path(d)/"fixture.gguf";model.write_bytes(b"mock only")
            observed=[]
            def runner(*args,**kwargs):
                observed.append(kwargs)
                data=b"\xff\xfe"
                return SimpleNamespace(returncode=0,stdout=data.decode(kwargs["encoding"],errors=kwargs["errors"])+"\u6743\u9650 \u6388\u6743",stderr="")
            result=revise("access-control-01",model,Path(d)/"record.json",runner=runner,max_attempts=1)
            self.assertEqual(observed[0]["errors"],"replace")
            self.assertIn("\ufffd",result["attempts"][0]["answer"])
            self.assertFalse(result["independent_completion_verified"])
    def test_no_false_success_on_model_failure(self):
        with tempfile.TemporaryDirectory() as d:
            model=Path(d)/"fixture.gguf";model.write_bytes(b"mock only")
            def runner(*args,**kwargs):
                return SimpleNamespace(returncode=1,stdout="",stderr="failure")
            with self.assertRaises(RuntimeError):
                revise("access-control-01",model,Path(d)/"record.json",runner=runner)
if __name__=="__main__": unittest.main()
