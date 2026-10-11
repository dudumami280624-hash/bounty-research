import unittest
from triage_reports import triage, render

class TriageTests(unittest.TestCase):
    def test_deduplicates_and_never_auto_verifies(self):
        item={"check":"reentrancy-eth","impact":"High","confidence":"Medium",
              "description":"src/Pay.sol: simulated unsafe ordering"}
        rows=triage({"projects":[{"name":"fixture","commit":"abc","findings":[item,item]}]})
        self.assertEqual(len(rows),1)
        self.assertEqual(rows[0]["priority"],"review")
        self.assertFalse(rows[0]["verified"])
        self.assertFalse(rows[0]["ready_to_submit"])
        self.assertEqual(rows[0]["reproduction"],"not_run")
        self.assertIn("UNVERIFIED",render(rows))
    def test_direct_scope_and_inherited_scope_are_separate(self):
        rows=triage({"projects":[{"commit":"abc","findings":[
            {"check":"a","impact":"High","description":"src/RewardAccumulator.sol: risky call"},
            {"check":"b","impact":"High","description":"src/Staker.sol: inherited call"},
            {"check":"c","impact":"High","description":"lib/thirdparty.sol: issue"}]}]})
        by_check={r["check"]:r for r in rows}
        self.assertEqual(by_check["a"]["scope_relevance"],"direct_in_scope_source")
        self.assertEqual(by_check["b"]["scope_relevance"],"inherited_impact_must_be_proven")
        self.assertEqual(by_check["c"]["scope_relevance"],"not_established")
        self.assertTrue(by_check["a"]["known_issue_review_required"])

    def test_defer_third_party_and_low_severity(self):
        rows=triage({"projects":[{"commit":"abc","findings":[
            {"check":"test","impact":"High","description":"lib/fixture.sol"},
            {"check":"style","impact":"Low","description":"src/M.sol"}]}]})
        self.assertTrue(all(x["priority"]=="deferred" for x in rows))

if __name__=="__main__": unittest.main()
