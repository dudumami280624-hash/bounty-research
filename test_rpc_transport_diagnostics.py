import unittest
import urllib.error
from rpc_transport_diagnostics import probe

class TransportTests(unittest.TestCase):
    def test_valid_chain(self):
        class Response:
            status=200
            def __enter__(self):return self
            def __exit__(self,*a):pass
            def read(self,n):return b'{"jsonrpc":"2.0","id":1,"result":"0x28751c"}'
        self.assertTrue(probe("https://rpc.example/",lambda req,timeout:Response())["usable"])
    def test_wrong_chain(self):
        class Response:
            status=200
            def __enter__(self):return self
            def __exit__(self,*a):pass
            def read(self,n):return b'{"result":"0x1"}'
        self.assertFalse(probe("https://rpc.example/",lambda req,timeout:Response())["usable"])
    def test_access_denied(self):
        def denied(req,timeout):
            raise urllib.error.HTTPError(req.full_url,403,"Forbidden",{},None)
        result=probe("https://rpc.example/",denied)
        self.assertEqual(result["category"],"access_denied")
        self.assertFalse(result["usable"])

if __name__=="__main__":
    unittest.main()
