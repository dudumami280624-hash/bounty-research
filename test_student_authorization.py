import tempfile
import unittest
from pathlib import Path
from student_authorization import Scope, authorize, require_authorization

class AuthorizationTests(unittest.TestCase):
    def test_approved_local_training(self):
        with tempfile.TemporaryDirectory() as d:
            scope=Scope("local-training", d, True)
            self.assertTrue(authorize(scope, str(Path(d)/"lesson.sol"), "local-poc"))
            self.assertTrue(authorize(scope, str(Path(d)/"lesson.sol"), "test"))
    def test_no_approval(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertFalse(authorize(Scope("local-training", d), str(Path(d)/"lesson.sol"), "test"))
    def test_outside_scope(self):
        with tempfile.TemporaryDirectory() as d:
            scope=Scope("local-training", str(Path(d)/"lab"), True)
            self.assertFalse(authorize(scope, str(Path(d)/"outside.sol"), "local-poc"))
    def test_external_targets_denied(self):
        self.assertFalse(authorize(Scope("external", "/tmp", True), "/tmp/target", "local-poc"))
    def test_prohibited_operations(self):
        with tempfile.TemporaryDirectory() as d:
            scope=Scope("local-training", d, True)
            for operation in ["attack", "scan-external", "exfiltrate", "shell"]:
                with self.assertRaises(PermissionError):
                    require_authorization(scope, str(Path(d)/"fixture.sol"), operation)

if __name__ == "__main__":
    unittest.main()
