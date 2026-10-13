import unittest
from research_capabilities import understanding,transfer,exploration

class CapabilityTests(unittest.TestCase):
    def test_understanding_requires_explanation(self):
        self.assertFalse(understanding({"root_cause":"external call"})["ready_for_review"])
        self.assertFalse(understanding({"root_cause":"a","invariant":"b","detection":"c","remediation":"d","source_url":"e"})["verified"])
    def test_transfer_rejects_repeated_families(self):
        with self.assertRaises(ValueError):
            transfer([{"family":"same","expected":True,"detected":True}]*2)
    def test_transfer_requires_independent_positive_negative(self):
        rows=[{"family":str(i),"expected":i<2,"detected":i<2} for i in range(4)]
        self.assertTrue(transfer(rows)["transfer_verified"])
        rows[2]["detected"]=True
        self.assertFalse(transfer(rows)["transfer_verified"])
    def test_exploration_not_claimed_without_evidence(self):
        self.assertFalse(exploration({"hypothesis":"test"})["testable"])
        self.assertFalse(exploration({"hypothesis":"a","derived_from":"b","independent_fixture":"c","falsification_condition":"d","scanner_evidence":"e","outcome":"f"})["discovery_verified"])
if __name__=="__main__":unittest.main()
