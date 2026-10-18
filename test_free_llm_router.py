"""Deterministic, network-free failover tests; no provider credentials needed."""
import io,json,os,tempfile,unittest,urllib.error
from unittest.mock import patch
from free_llm_router import Provider,load_providers,route,NoFreeProviderAvailable

A=Provider("free-a","https://example.org/v1","model-a","FREE_A_KEY")
B=Provider("free-b","https://example.net/v1","model-b","FREE_B_KEY")

class RouterTests(unittest.TestCase):
    def test_rate_limit_switches_provider(self):
        calls=[]
        def fake(p,m):
            calls.append(p.name)
            if p.name=="free-a":
                raise urllib.error.HTTPError("https://example.org",429,"rate limit",{},None)
            return {"choices":[{"message":{"content":"ok"}}],"usage":{"prompt_tokens":7,"completion_tokens":2}}
        with tempfile.TemporaryDirectory() as d,patch.dict(os.environ,{"FREE_A_KEY":"test","FREE_B_KEY":"test"}):
            result=route([{"role":"user","content":"test"}],[A,B],transport=fake,log_path=d+"/log.jsonl")
            self.assertEqual(result["provider"],"free-b")
            self.assertEqual(calls,["free-a","free-b"])
            logs=[json.loads(x) for x in open(d+"/log.jsonl",encoding="utf-8")]
            self.assertEqual(logs[0]["status"],429)
            self.assertEqual(logs[1]["prompt_tokens"],7)
    def test_missing_keys_do_not_call_network(self):
        with tempfile.TemporaryDirectory() as d,patch.dict(os.environ,{"FREE_A_KEY":"","FREE_B_KEY":""}):
            with self.assertRaises(NoFreeProviderAvailable):
                route([], [A,B],transport=lambda p,m:self.fail("unexpected call"),log_path=d+"/log.jsonl")
    def test_paid_provider_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path=d+"/config.json"
            with open(path,"w") as f: json.dump({"providers":[dict(name="paid",base_url="https://example.org/v1",model="x",api_key_env="K",free_only=False)]},f)
            with self.assertRaises(ValueError): load_providers(path)
    def test_unsafe_url_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            path=d+"/config.json"
            with open(path,"w") as f: json.dump({"providers":[dict(name="unsafe",base_url="http://example.org/v1",model="x",api_key_env="K")]},f)
            with self.assertRaises(ValueError): load_providers(path)
if __name__=="__main__":unittest.main()
