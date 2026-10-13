import unittest
from research_prioritizer import rank_targets
from research_metrics import ratio, summarize
from research_triage import assess

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

    def test_missing_independent_review_blocks(self):
        self.assertIn("independent_review", assess({})["missing_evidence"])

if __name__ == "__main__":
    unittest.main()
