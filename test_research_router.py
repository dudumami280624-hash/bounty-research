import unittest
from research_router import eligible, select_path, transition


def path(**changes):
    p = dict(id="a", channel="contract", scope_verified=True,
             authorization_verified=True, evidence=["official-scope-reference"],
             last_updated="2026-10-12", priority=5, status="review", stale_cycles=0)
    p.update(changes)
    return p


class RouterTests(unittest.TestCase):
    def test_valid(self):
        self.assertTrue(eligible(path()))
    def test_missing_authorization(self):
        self.assertFalse(eligible(path(authorization_verified=False)))
    def test_missing_scope(self):
        self.assertFalse(eligible(path(scope_verified=False)))
    def test_no_evidence(self):
        self.assertFalse(eligible(path(evidence=[])))
    def test_invalid_channel(self):
        self.assertFalse(eligible(path(channel="other")))
    def test_priority_and_tie(self):
        self.assertEqual(select_path([path(id="b"), path(id="a")])["id"], "a")
    def test_skip_blocked(self):
        self.assertEqual(select_path([path(id="a", status="blocked"), path(id="b")])["id"], "b")
    def test_all_blocked(self):
        self.assertIsNone(select_path([path(stale_cycles=2)]))
    def test_two_cycles_block(self):
        self.assertEqual(transition(transition(path()))["status"], "blocked")
    def test_reopen_with_evidence(self):
        self.assertEqual(transition(path(status="blocked", stale_cycles=2), new_evidence=True)["status"], "review")
    def test_no_evidence_no_reopen(self):
        with self.assertRaises(ValueError):
            transition(path(status="blocked", evidence=[]), new_evidence=True)


if __name__ == "__main__":
    unittest.main()
