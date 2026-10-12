import unittest
from acceptance import evaluate

def base():
    return {
       "audit.json":{"projects":[{"status":"source retrieved; heuristic review only"}]},
       "slither_results.json":{"projects":[{"status":"analyzed"}]},
       "eligibility_status.json":{"officially_verified_targets":0},
       "triage_results.json":{"ready_to_submit":0},
       "lead_verification.json":{"verified_vulnerabilities":0,"cases":[]},
       "specific_poc_results.json":{"execution":"passed","tests_passed":6,
                                     "conditional_simulation_only":True,"real_world_exploit_verified":False},
       "submission_status.json":{"approved_for_submission":0,"actual_submissions":0,
                                 "payout_confirmed_usd":0}
    }

class AcceptanceTests(unittest.TestCase):
    def test_green_scanner_synthetic_poc_not_full_acceptance(self):
        result=evaluate(base())
        self.assertEqual(result["passed"],1)
        self.assertFalse(result["full_acceptance"])
        self.assertEqual(result["business_outcomes"]["verified_vulnerabilities"],0)
    def test_fail_closed_without_source(self):
        self.assertEqual(evaluate({})["passed"],0)
    def test_verified_scope_no_fabricated_submission(self):
        d=base()
        d["eligibility_status.json"]["officially_verified_targets"]=1
        d["lead_verification.json"]={"verified_vulnerabilities":1,"cases":[{"verified":True}]}
        d["specific_poc_results.json"]["real_world_exploit_verified"]=True
        d["triage_results.json"]["ready_to_submit"]=1
        d["submission_status.json"]["approved_for_submission"]=1
        result=evaluate(d)
        self.assertEqual(result["passed"],4)
        self.assertFalse(result["full_acceptance"])
    def test_real_official_receipt_and_status_required(self):
        d=base()
        d["eligibility_status.json"].update({"officially_verified_targets":1,
                                           "official_report_statuses":[{"id":"fixture","status":"pending"}]})
        d["lead_verification.json"]={"verified_vulnerabilities":1,"cases":[{"verified":True}]}
        d["specific_poc_results.json"]["real_world_exploit_verified"]=True
        d["triage_results.json"]["ready_to_submit"]=1
        d["submission_status.json"].update({"approved_for_submission":1,"actual_submissions":1,
                                           "official_receipts":[{"id":"fixture"}]})
        self.assertEqual(evaluate(d)["passed"],6)
if __name__=="__main__":unittest.main()
