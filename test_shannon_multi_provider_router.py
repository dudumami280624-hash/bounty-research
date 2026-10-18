import tempfile
import unittest
from unittest.mock import patch
from pathlib import Path
from shannon_multi_provider_router import route, candidates

class RoutingTests(unittest.TestCase):
    def setUp(self):
        self.key_patch = patch.dict('os.environ', {'SHANNON_AI_API_KEY': 'test-only-placeholder'})
        self.key_patch.start()
        self.addCleanup(self.key_patch.stop)

    def test_fallback_on_quota(self):
        config={"candidates":[{"model":"groq:first"},{"model":"openrouter:second"}]}
        seen=[]
        def attempt(c):
            seen.append(c["model"])
            return (1,"usage limit") if len(seen)==1 else (0,"OK")
        with tempfile.TemporaryDirectory() as d:
            r=route(config,attempt,Path(d)/"evidence.json")
        self.assertEqual(r["selected_model"],"openrouter:second")
        self.assertFalse(r["full_shannon_scan_verified"])
        self.assertFalse(r["unlimited_free_verified"])
    def test_nonretryable_stops(self):
        config={"candidates":[{"model":"groq:first"},{"model":"openrouter:second"}]}
        with tempfile.TemporaryDirectory() as d:
            r=route(config,lambda c:(1,"invalid API key"),Path(d)/"e.json")
        self.assertIsNone(r["selected_model"])
        self.assertEqual(len(r["attempts"]),1)
    def test_codex_skipped(self):
        config={"candidates":[{"model":"openai-codex:gpt-6.1-sol","pi_auth":True},{"model":"groq:other"}]}
        with tempfile.TemporaryDirectory() as d:
            r=route(config,lambda c:(0,"OK"),Path(d)/"e.json")
        self.assertEqual(r["selected_model"],"groq:other")
        self.assertEqual(r["attempts"][0]["status"],"skipped_preflight")
    def test_duplicate_rejected(self):
        with self.assertRaises(ValueError):
            list(candidates({"candidates":[{"model":"a:b"},{"model":"a:b"}]}))
if __name__=="__main__":
    unittest.main()
