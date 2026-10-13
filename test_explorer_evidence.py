import unittest
from explorer_evidence import inspect,DEPLOYMENTS

class ExplorerEvidenceTests(unittest.TestCase):
    def test_verified_rest_never_claims_fork(self):
        def read(path):
            if path=="/stats":return {"total_blocks":"100"}
            address=path.rsplit("/",1)[-1]
            return {"hash":address,"is_contract":True}
        result=inspect(read)
        self.assertTrue(result["verified"])
        self.assertFalse(result["fork_compatible"])
        self.assertEqual(result["seven_fork_tests_passed"],0)
    def test_mismatched_address_fails_closed(self):
        def read(path):
            return {"total_blocks":"100"} if path=="/stats" else {"hash":"0xwrong","is_contract":True}
        self.assertFalse(inspect(read)["verified"])
    def test_denied_endpoint_records_unavailable(self):
        def read(path):raise ValueError("unavailable")
        self.assertEqual(inspect(read)["status"],"rest_unavailable")

if __name__=="__main__":
    unittest.main()
