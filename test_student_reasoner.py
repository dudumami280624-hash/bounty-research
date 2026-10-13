import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from student_reasoner import local_inference

class ReasonerTests(unittest.TestCase):
    def test_missing_model_never_claims_inference(self):
        with tempfile.TemporaryDirectory() as d:
            with self.assertRaises(FileNotFoundError):
                local_inference("reentrancy-01",Path(d)/"missing.gguf",Path(d)/"out.json")
            self.assertFalse((Path(d)/"out.json").exists())
    def test_model_failure_never_records_success(self):
        with tempfile.TemporaryDirectory() as d:
            model=Path(d)/"dummy.gguf"
            model.write_bytes(b"fixture")
            def fail(*args,**kwargs):
                return SimpleNamespace(returncode=1,stdout="",stderr="error")
            with self.assertRaises(RuntimeError):
                local_inference("reentrancy-01",model,Path(d)/"out.json",runner=fail)
    def test_mock_output_is_only_a_unit_test_not_real_inference(self):
        with tempfile.TemporaryDirectory() as d:
            model=Path(d)/"dummy.gguf"
            model.write_bytes(b"fixture")
            def fake(*args,**kwargs):
                return SimpleNamespace(returncode=0,stdout="先更新状态，再执行外部调用",stderr="")
            record=local_inference("reentrancy-01",model,Path(d)/"out.json",runner=fake)
            self.assertFalse(record["agent"]["independent_completion_verified"])
            self.assertEqual(len(record["attempts"]),1)
if __name__=="__main__":
    unittest.main()
