import unittest
from shannon_provider_preflight import inspect

class ProviderPreflightTests(unittest.TestCase):
    def test_exhausted_codex_is_not_unlimited(self):
        result = inspect("openai-codex:gpt-6.1-sol", use_pi_auth=True)
        self.assertFalse(result["ready_for_remote_validation"])
        self.assertFalse(result["unlimited_free_verified"])
    def test_missing_credential_is_rejected(self):
        self.assertFalse(inspect("openrouter:example/free")["ready_for_remote_validation"])
    def test_key_does_not_prove_unlimited_free(self):
        result = inspect("groq:example", api_key="dummy")
        self.assertTrue(result["ready_for_remote_validation"])
        self.assertFalse(result["remote_model_verified"])
        self.assertFalse(result["unlimited_free_verified"])
    def test_bad_model_spec_is_rejected(self):
        self.assertFalse(inspect("invalid", api_key="dummy")["ready_for_remote_validation"])

if __name__ == "__main__":
    unittest.main()
