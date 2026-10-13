import unittest
from unittest.mock import patch
import urllib.error
import run_deployment_fork as m

class RpcFailoverTests(unittest.TestCase):
    def test_falls_back_after_http_403(self):
        calls=[]
        def fake_snapshot(read):
            read("eth_chainId", [])
            return {"fork_block_number":123}
        def fake_read(method,params,rpc_url=None):
            calls.append(rpc_url)
            if rpc_url==m.RPC_ENDPOINTS[0]:
                raise urllib.error.HTTPError(rpc_url,403,"forbidden",None,None)
            return "0x2874bc"
        with patch.object(m,"deployment_snapshot",side_effect=fake_snapshot),patch.object(m,"rpc_read",side_effect=fake_read):
            endpoint,snapshot=m.select_rpc_snapshot()
        self.assertEqual(endpoint,m.RPC_ENDPOINTS[1])
        self.assertEqual(snapshot["fork_block_number"],123)
        self.assertEqual(calls,m.RPC_ENDPOINTS[:2])

    def test_all_endpoints_failed_never_claims_validation(self):
        with patch.object(m,"deployment_snapshot",side_effect=urllib.error.HTTPError("url",403,"forbidden",None,None)):
            with self.assertRaisesRegex(RuntimeError,"No configured/public RPC passed deployment verification") as ctx:
                m.select_rpc_snapshot()
        self.assertIn('"http_status": 403',str(ctx.exception))

    def test_invalid_chain_rejected(self):
        with self.assertRaisesRegex(ValueError,"Unexpected chain"):
            m.deployment_snapshot(lambda method,params:"0x1")

if __name__=="__main__":
    unittest.main()
