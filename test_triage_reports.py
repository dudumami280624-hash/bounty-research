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
    def test_defer_third_party_and_low_severity(self):
        rows=triage({"projects":[{"commit":"abc","findings":[
            {"check":"test","impact":"High","description":"lib/fixture.sol"},
            {"check":"style","impact":"Low","description":"src/M.sol"}]}]})
        self.assertTrue(all(x["priority"]=="deferred" for x in rows))

if __name__=="__main__": unittest.main()
