"""Regression tests for offline scope validation (no network operations)."""
import unittest
from research_scope_guard import scope_is_current


class ScopeGuardSmokeTest(unittest.TestCase):
    def test_unverified_scope_fails_closed(self):
        self.assertFalse(scope_is_current({}))


if __name__ == "__main__":
    unittest.main()
