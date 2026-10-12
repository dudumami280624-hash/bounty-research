import unittest
from datetime import datetime, timezone, timedelta
from duplicate_gate import duplicate_gate

COMMIT="ab92502e9da98784dfe3bd3ef933d4e9345ff628"
def good():
    return {"duplicate_review":{
        "decision":"clear","same_root_cause_found":False,"known_issue_found":False,
        "independent_reviewer_approved":True,"source_commit":COMMIT,
        "checked_at_utc":datetime.now(timezone.utc).isoformat(),
        "sources_checked":{k:{"checked":True,"evidence":"reviewed public source URL and root cause"}
                           for k in ("official_known_issues","public_disclosures","repository_history","public_audits")},
        "root_cause_fingerprint":"contract/function/trigger/fix",
        "private_reports_visibility":"unknown"}}

class DuplicateGateTests(unittest.TestCase):
    def test_missing_review_blocks(self):
        self.assertEqual(duplicate_gate({},{"commit":COMMIT})[0],False)
    def test_full_review_allows_draft_only(self):
        self.assertEqual(duplicate_gate(good(),{"commit":COMMIT})[0],True)
    def test_same_root_cause_blocks(self):
        x=good();x["duplicate_review"]["same_root_cause_found"]=True
        self.assertFalse(duplicate_gate(x,{"commit":COMMIT})[0])
    def test_missing_source_blocks(self):
        x=good();del x["duplicate_review"]["sources_checked"]["public_audits"]
        self.assertFalse(duplicate_gate(x,{"commit":COMMIT})[0])
    def test_stale_review_blocks(self):
        x=good();x["duplicate_review"]["checked_at_utc"]=(datetime.now(timezone.utc)-timedelta(days=9)).isoformat()
        self.assertFalse(duplicate_gate(x,{"commit":COMMIT})[0])
    def test_mismatched_commit_blocks(self):
        self.assertFalse(duplicate_gate(good(),{"commit":"different"})[0])
    def test_unknown_private_reports_required(self):
        x=good();x["duplicate_review"]["private_reports_visibility"]="clear"
        self.assertFalse(duplicate_gate(x,{"commit":COMMIT})[0])

if __name__=="__main__":unittest.main()
