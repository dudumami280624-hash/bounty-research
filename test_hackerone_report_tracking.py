import unittest
from hackerone_report_tracking import parse_page, summarize

class ReportSyncTests(unittest.TestCase):
 def test_empty_provider_response_is_successful_empty_sync(self):
  entries,url=parse_page({"data":[],"links":{"next":None}})
  self.assertEqual(entries,[])
  self.assertIsNone(url)
  summary=summarize([{"data":[],"links":{"next":None}}])
  self.assertEqual(summary["reports_seen"],0)
  self.assertEqual(summary["payouts_verified_usd"],0)
 def test_report_statuses_not_payments(self):
  data={"data":[{"id":"123","type":"report",
          "attributes":{"state":"triaged","title":"Never disclose title",
                        "bounty_amount":999999}},
                 {"id":"124","attributes":{"state":"resolved"}}]}
  summary=summarize([data])
  self.assertEqual(summary["report_states"],{"triaged":1,"resolved":1})
  self.assertEqual(summary["payouts_verified_usd"],0)
  self.assertNotIn("title",str(summary))
  self.assertNotIn("999999",str(summary))
 def test_untrusted_links_and_malformed_provider_data_fail(self):
  with self.assertRaises(ValueError):
   parse_page({"data":[],"links":{"next":"https://attacker.example/"}})
  with self.assertRaises(ValueError):
   parse_page({"data":[{"id":"not an id"}]})
 def test_unknown_state_stays_unknown(self):
  records,_=parse_page({"data":[{"id":"42","attributes":{"state":"awarded-a-billion"}}]})
  self.assertEqual(records[0]["state"],"unknown")
if __name__=="__main__":unittest.main()
