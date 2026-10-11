import unittest
from bugcrowd_bounties import select_bugcrowd_candidates

class BugcrowdDiscoveryTests(unittest.TestCase):
    def test_filter_deduplicate_and_flag_unverified(self):
        src={"error":None,"candidates":[
            {"name":"Bitso","program_url":"https://bugcrowd.com/engagements/bitso-mbb-og","catalog_marks_bounty":True},
            {"name":"Bitso duplicate","program_url":"https://www.bugcrowd.com/engagements/bitso-mbb-og/","catalog_marks_bounty":True},
            {"name":"Other","program_url":"https://hackerone.com/demo","catalog_marks_bounty":True},
            {"name":"VDP","program_url":"https://bugcrowd.com/engagements/demo","catalog_marks_bounty":False},
            {"name":"Spoof","program_url":"https://bugcrowd.com.bad.example/x","catalog_marks_bounty":True},
        ]}
        items=select_bugcrowd_candidates(src)
        self.assertEqual(len(items),1)
        self.assertFalse(items[0]["official_scope_verified"])
        self.assertFalse(items[0]["cash_amount_verified"])
    def test_fail_closed_on_source_error(self):
        with self.assertRaises(ValueError):
            select_bugcrowd_candidates({"error":"offline","candidates":[]})
if __name__=="__main__":
    unittest.main()
