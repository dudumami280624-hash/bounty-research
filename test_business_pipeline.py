"""End-to-end OFFLINE fixture: proves components work, never counts as a live bounty."""
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from acceptance import evaluate
from build_verified_reports import COMMIT,generate
from submission_gate import ready
from hackerone_report_tracking import summarize
from verify_official_scope import validate_pages,EXPECTED_INFO,EXPECTED_SCOPE

class FullPipelineIntegration(unittest.TestCase):
 def test_six_components_interoperate_without_any_live_submission(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp)
   (root/"evidence").mkdir()
   (root/"evidence"/"repro.log").write_text("OFFLINE TEST FIXTURE: intentionally not real security evidence\n")
   scope_evidence={"information_url":EXPECTED_INFO,"scope_url":EXPECTED_SCOPE,
      "pinned_commit":COMMIT,
      "direct_source_assets":["src/ZenStaker.sol","src/RewardAccumulator.sol"]}
   info="Horizen Maximum Bounty $10,000 Submit a Bug Runnable PoC Required Rewards in USDC"
   scoped="Horizen Assets in Scope ZenStaker RewardAccumulator ab92502 Submit a Bug"
   is_scoped,_=validate_pages(scope_evidence,info,scoped)
   self.assertTrue(is_scoped)
   triage={"findings":[{"id":"fixture-1","commit":COMMIT,"description":"test fixture only"}]}
   lead={"id":"fixture-1","verified":True,"poc_status":"finding_specific_poc_passed",
       "bounty_scope_verified":True,"known_issue_checked":True,"impact_verified":True,
       "poc_passed":True,"title":"Offline fixture, not a real bug",
       "security_impact":"Synthetic controlled impact",
       "reproduction_steps":"python -m unittest test_business_pipeline.py",
       "fix_recommendation":"No change to real production contract",
       "evidence_path":"evidence/repro.log","explicit_submission_approved":False}
   verified={"cases":[lead],"verified_vulnerabilities":1}
   fake_poc={"execution":"passed","source_commit":COMMIT,
             "conditional_simulation_only":False,"real_world_exploit_verified":True}
   official={"status":"verified","verified_count":1,"pinned_commit":COMMIT}
   output=generate(triage,verified,fake_poc,official,root)
   self.assertEqual(output["verified_reports_generated"],0)
   self.assertTrue(output["blocked"])
   with patch("submission_gate.ROOT",root):
    self.assertFalse(ready(lead))
    lead["explicit_submission_approved"]=True
    self.assertTrue(ready(lead))
   self.assertFalse((root/"reports").exists())
   states=summarize([{"data":[{"id":"123","attributes":{"state":"triaged"}}]}])
   self.assertEqual(states["report_states"],{"triaged":1})
   self.assertEqual(states["payouts_verified_usd"],0)
   # Only fixture flags below. Never publish this as a real-world result.
   mock_records={
    "eligibility_status.json":{"officially_verified_targets":1,
       "official_report_statuses":[{"id":"123","state":"triaged"}]},
    "audit.json":{"projects":[{"status":"source retrieved; heuristic review only"}]},
    "slither_results.json":{"projects":[{"status":"analyzed"}]},
    "triage_results.json":{"ready_to_submit":1},
    "lead_verification.json":verified,
    "specific_poc_results.json":fake_poc,
    "report_build_status.json":output,
    "submission_status.json":{"approved_for_submission":1,
       "actual_submissions":1,"official_receipts":[{"id":"123"}],
       "payout_confirmed_usd":0},
   }
   self.assertTrue(evaluate(mock_records)["full_acceptance"])
   # But without fake official receipt, stage 5 and 6 MUST fail.
   mock_records["submission_status.json"]["actual_submissions"]=0
   mock_records["submission_status.json"]["official_receipts"]=[]
   self.assertFalse(evaluate(mock_records)["full_acceptance"])
   self.assertEqual(evaluate(mock_records)["passed"],4)
 def test_synthetic_actual_poc_does_not_generate_real_report(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp)
   triage={"findings":[{"id":"x","commit":COMMIT}]}
   leads={"cases":[{"id":"x","verified":True}]}
   poc={"execution":"passed","conditional_simulation_only":True,
        "real_world_exploit_verified":False,"source_commit":COMMIT}
   scope={"status":"verified","verified_count":1,"pinned_commit":COMMIT}
   result=generate(triage,leads,poc,scope,root)
   self.assertEqual(result["verified_reports_generated"],0)
if __name__=="__main__":unittest.main()
