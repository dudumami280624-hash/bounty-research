"""Evidence-producing exploit regression on a fully local synthetic fixture."""
import hashlib,json,unittest
from datetime import datetime,timezone
from pathlib import Path
from labs.offline_idor_lab import vulnerable_read,protected_read

class OfflineAccessControlTests(unittest.TestCase):
    def test_owner_can_read(self):
        self.assertEqual(protected_read("alice","doc-a"),"alice private")

    def test_cross_user_vulnerability_reproduces(self):
        # This test PASSES only if the deliberately vulnerable implementation leaks.
        self.assertEqual(vulnerable_read("alice","doc-b"),"bob private")

    def test_fixed_implementation_blocks_cross_user(self):
        with self.assertRaises(PermissionError):
            protected_read("alice","doc-b")

if __name__=="__main__":
    import io
    stream=io.StringIO()
    suite=unittest.defaultTestLoader.loadTestsFromTestCase(OfflineAccessControlTests)
    result=unittest.TextTestRunner(stream=stream,verbosity=2).run(suite)
    evidence={"lab":"synthetic-offline-idor","source_sha256":hashlib.sha256(Path("labs/offline_idor_lab.py").read_bytes()).hexdigest(),
              "tests_run":result.testsRun,"failures":len(result.failures),"errors":len(result.errors),
              "vulnerability_reproduced":result.wasSuccessful(),"fixed_behavior_tested":result.wasSuccessful(),
              "real_world_vulnerability_verified":False,"model_independently_discovered":False,
              "test_output":stream.getvalue()}
    out=Path("child-evidence/offline-idor-lab.json");out.parent.mkdir(exist_ok=True)
    out.write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(stream.getvalue());print(json.dumps({k:v for k,v in evidence.items() if k!="test_output"}))
    raise SystemExit(0 if result.wasSuccessful() else 1)
