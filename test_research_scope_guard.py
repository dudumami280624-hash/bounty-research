"""Regression tests for offline scope validation (no network operations)."""
import unittest
from datetime import datetime, timezone
from research_scope_guard import scope_check_is_current


class ScopeGuardSmokeTest(unittest.TestCase):
    def test_unverified_scope_fails_closed(self):
        self.assertFalse(scope_check_is_current({}))

    def test_scope_missing_required_evidence_fails_closed(self):
        now = datetime(2026, 10, 13, tzinfo=timezone.utc)
        valid = {
            "status": "verified",
            "cash_bounty_verified": True,
            "official_scope_url": "https://example.org/official-scope",
            "verified_at_utc": "2026-10-13T00:00:00+00:00",
        }
        for key in valid:
            invalid = dict(valid)
            invalid.pop(key)
            with self.subTest(missing=key):
                self.assertFalse(scope_check_is_current(invalid, now=now))
        invalid = dict(valid, official_scope_url="http://example.org/scope")
        self.assertFalse(scope_check_is_current(invalid, now=now))
        invalid = dict(valid, verified_at_utc="2026-10-13T00:00:00")
        self.assertFalse(scope_check_is_current(invalid, now=now))
        invalid = dict(valid, verified_at_utc="not-a-date")
        self.assertFalse(scope_check_is_current(invalid, now=now))

    def test_verified_scope_requires_fresh_timestamp(self):
        now = datetime(2026, 10, 13, tzinfo=timezone.utc)
        record = {
            "status": "verified",
            "cash_bounty_verified": True,
            "official_scope_url": "https://example.org/official-scope",
            "verified_at_utc": "2026-10-13T00:00:00+00:00",
        }
        self.assertTrue(scope_check_is_current(record, now=now))
        record["verified_at_utc"] = "2026-10-11T00:00:00+00:00"
        self.assertFalse(scope_check_is_current(record, now=now))


if __name__ == "__main__":
    unittest.main()
