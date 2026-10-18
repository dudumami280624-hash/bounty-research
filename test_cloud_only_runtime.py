"""Offline tests for the cloud-only runtime. No API calls and no local inference."""
import contextlib,io,json,tempfile,unittest
from unittest.mock import patch
import cloud_only_runtime
from free_llm_router import NoFreeProviderAvailable

class CloudOnlyRuntimeTests(unittest.TestCase):
    def test_empty_provider_config_fails_closed(self):
        with tempfile.TemporaryDirectory() as d:
            path=d+"/config.json"
            with open(path,"w") as f: json.dump({"providers":[]},f)
            with patch("sys.argv",["cloud_only_runtime.py","--config",path]):
                with contextlib.redirect_stdout(io.StringIO()) as out:
                    code=cloud_only_runtime.main()
            self.assertEqual(code,2)
            self.assertIn("blocked",out.getvalue())
    def test_exhausted_free_pool_never_falls_back(self):
        with tempfile.TemporaryDirectory() as d:
            path=d+"/config.json"
            with open(path,"w") as f:
                json.dump({"providers":[{"name":"free","base_url":"https://example.org/v1","model":"free-model","api_key_env":"FREE_TEST_KEY"}]},f)
            with patch("sys.argv",["cloud_only_runtime.py","--config",path]):
                with patch.object(cloud_only_runtime,"route",side_effect=NoFreeProviderAvailable("429")):
                    with contextlib.redirect_stdout(io.StringIO()) as out:
                        code=cloud_only_runtime.main()
            self.assertEqual(code,3)
            self.assertIn("no local or paid fallback",out.getvalue())
if __name__=="__main__": unittest.main()
