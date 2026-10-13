import unittest
from research_prioritizer import rank_targets
from research_metrics import ratio, summarize
from research_triage import assess
from research_cycle import evaluate_cycle

class ResearchUpgradeTests(unittest.TestCase):
    def test_scope_is_mandatory(self):
        candidates = [{"name": "unauthorized", "official_scope_verified": True},
                      {"name": "allowed", "official_scope_verified": True,
                       "testing_authorized": True, "source_pinned": True}]
        self.assertEqual([x["name"] for x in rank_targets(candidates)], ["allowed"])

    def test_unknown_denominator_is_not_zero(self):
        self.assertIsNone(ratio(0, 0))
        self.assertIsNone(summarize({})["confirmed_finding_rate"])

    def test_invalid_metric_counts_rejected(self):
        with self.assertRaises(ValueError):
            ratio(2, 1)

    def test_simulated_lead_never_verifies(self):
        evidence = {key: True for key in
                    ("pinned_source", "scope_verified", "attacker_control", "reachable",
                     "impact_evidence", "reproduction_log", "known_issue_checked",
                     "independent_review")}
        evidence["synthetic_only"] = True
        self.assertFalse(assess(evidence)["candidate_verified"])
        self.assertFalse(assess(evidence)["may_submit"])

    def test_six_step_cycle_requires_evidence(self):
        result = evaluate_cycle({})
        self.assertFalse(result["engineering_cycle_complete"])
        self.assertFalse(result["real_world_vulnerability_verified"])
        self.assertIn("replay_log", result["steps"]["historical_replay"]["missing"])

    def test_synthetic_replay_cannot_authorize_submission(self):
        record = {
            "collect": {"source_url": "https://example.org", "source_type": "public", "license_reviewed": True},
            "root_cause": {"affected_component": "fixture", "root_cause": "test", "security_invariant": "balance"},
            "historical_replay": {"vulnerable_revision": "a", "fixed_revision": "b", "replay_log": "fixture.log"},
            "adapt_detector": {"detector_path": "fixture.py", "positive_fixture": "positive", "negative_fixture": "negative"},
            "authorized_validation": {"official_scope_url": "https://example.org/scope", "scope_verified": False, "testing_authorized": False, "pinned_revision": "c", "validation_log": "fixture.log"},
            "feedback": {"outcome": "synthetic", "limitations": "fixture only", "next_action": "real replay"},
        }
        result = evaluate_cycle(record)
        self.assertFalse(result["engineering_cycle_complete"])
        self.assertFalse(result["submission_authorized"])

    def test_missing_independent_review_blocks(self):
        self.assertIn("independent_review", assess({})["missing_evidence"])

if __name__ == "__main__":
    unittest.main()
