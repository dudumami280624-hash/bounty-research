import unittest
from bounty_intake import parse_snapshot

class TestBountyIntake(unittest.TestCase):
    def test_unverified_lead_only(self):
        data = parse_snapshot("<html><head><title>Example Program</title></head></html>", "https://example.org/bounty")
        self.assertEqual(data["page_title"], "Example Program")
        self.assertFalse(data["official_scope_verified"])
        self.assertFalse(data["vulnerability_verified"])
        self.assertFalse(data["ready_to_submit"])
        self.assertEqual(data["payout_verified_usd"], 0)

    def test_reject_non_http_source(self):
        with self.assertRaises(ValueError):
            parse_snapshot("<title>x</title>", "file:///tmp/a")

if __name__ == "__main__":
    unittest.main()
