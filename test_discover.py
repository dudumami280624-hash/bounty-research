import unittest
from discover import discover

class CandidateDiscoveryTests(unittest.TestCase):
    def test_repo_filter_and_dedup(self):
        data = [{"slug": "sample", "assets": [
            {"url": "https://github.com/example/contract/blob/main/src/T.sol"},
            {"url": "https://github.com/example/contract"},
            {"url": "https://evil.example/other"},
        ]}]
        result = discover(data)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["repository"], "https://github.com/example/contract")
        self.assertIn("UNVERIFIED", result[0]["status"])

    def test_invalid_payload(self):
        with self.assertRaises(ValueError):
            discover({})

    def test_no_auto_approval(self):
        result = discover([{"name":"Demo","assets":[{"url":"https://github.com/demo/repo"}]}])
        self.assertNotIn("approved", result[0])

if __name__ == "__main__":
    unittest.main()
