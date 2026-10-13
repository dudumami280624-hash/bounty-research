import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from build_verified_reports import generate, COMMIT

def fixture(root):
    (root/"evidence").mkdir()
    (root/"evidence"/"local.txt").write_text("repro command and console proof\n")
    triage={"findings":[{"id":"fixture-a","commit":COMMIT,
                         "description":"RewardAccumulator.sendRewardsToStaker()"}]}
    case={"id":"fixture-a","verified":True,"poc_status":"finding_specific_poc_passed",
          "verified":True,"bounty_scope_verified":True,"known_issue_checked":True,
          "impact_verified":True,"poc_passed":True,
          "title":"Locally verified test fixture","security_impact":"Validated impact fixture",
          "reproduction_steps":"Local forge test fixture",
          "fix_recommendation":"Apply appropriate access guard",
          "evidence_path":"evidence/local.txt"}
    poc={"execution":"passed","real_world_exploit_verified":True,
         "conditional_simulation_only":False,"source_commit":COMMIT}
    scope={"status":"verified","verified_count":1,"pinned_commit":COMMIT}
    return triage,{"cases":[case]},poc,scope

class VerifiedReportBuilderTests(unittest.TestCase):
 def test_unreviewed_fixture_cannot_generate_report(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp)
   triage,leads,poc,scope=fixture(root)
   result=generate(triage,leads,poc,scope,root)
   self.assertEqual(result["verified_reports_generated"],0)
   self.assertFalse((root/"reports").exists())
   self.assertTrue(result["blocked"])
 def test_reviewed_draft_still_never_submits(self):
  # Positive-path fixture only: mock the review decision, never production evidence.
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp); triage,leads,poc,scope=fixture(root)
   with patch("build_verified_reports.duplicate_gate", return_value=(True,"synthetic_test_only")):
    result=generate(triage,leads,poc,scope,root)
   self.assertEqual(result["verified_reports_generated"],1)
   self.assertFalse(result["reports"][0]["submitted"])
   self.assertIn("NOT SENT",(root/result["reports"][0]["path"]).read_text())

 def test_synthetic_poc_never_creates_report(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp); triage,leads,poc,scope=fixture(root)
   poc["conditional_simulation_only"]=True
   self.assertEqual(generate(triage,leads,poc,scope,root)["verified_reports_generated"],0)
   self.assertFalse((root/"reports").exists())
 def test_missing_evidence_and_path_escape_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);triage,leads,poc,scope=fixture(root)
   leads["cases"][0]["evidence_path"]="evidence/../outside.txt"
   self.assertEqual(generate(triage,leads,poc,scope,root)["verified_reports_generated"],0)
   leads["cases"][0]["evidence_path"]="evidence/missing.txt"
   self.assertEqual(generate(triage,leads,poc,scope,root)["verified_reports_generated"],0)
 def test_report_filename_cannot_escape_reports_directory(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp); triage,leads,poc,scope=fixture(root)
   dangerous="../escape"
   triage["findings"][0]["id"]=dangerous
   leads["cases"][0]["id"]=dangerous
   result=generate(triage,leads,poc,scope,root)
   self.assertEqual(result["verified_reports_generated"],0)
   self.assertEqual(result["blocked"][0]["reason"],"unsafe_finding_identifier")
   self.assertFalse((root/"escape.md").exists())
 def test_unverified_or_unmatched_source_rejected(self):
  with tempfile.TemporaryDirectory() as tmp:
   root=Path(tmp);triage,leads,poc,scope=fixture(root)
   scope["verified_count"]=0
   self.assertEqual(generate(triage,leads,poc,scope,root)["verified_reports_generated"],0)
   scope["verified_count"]=1
   triage["findings"][0]["commit"]="wrong"
   self.assertEqual(generate(triage,leads,poc,scope,root)["verified_reports_generated"],0)
if __name__=="__main__":unittest.main()
