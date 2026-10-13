import json,tempfile,unittest
from pathlib import Path
from knowledge_detector_bridge import correlate

class KnowledgeDetectorBridgeTests(unittest.TestCase):
    def test_scanner_evidence_required_and_matched(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d); k=p/"index.json";s=p/"scan.json"
            k.write_text(json.dumps({"curated:a":{"source":"curated-case","category":"reentrancy","root_cause":"reentrancy external call","invariant":"balances update before external call","detection":"reentrancy-eth","verification":"unverified"},"ghsa:b":{"source":"github-reviewed-advisory","title":"reentrancy"}}))
            s.write_text(json.dumps({"projects":[{"name":"lab","findings":[{"check":"reentrancy-eth","description":"External call before balance update","impact":"High","locations":[{"path":"src/Lab.sol","lines":[12]}]}]}]}))
            r=correlate(k,s)
            self.assertEqual(r["scanner_findings"],1)
            self.assertEqual(r["correlated_findings"],1)
            self.assertEqual(r["findings"][0]["knowledge_matches"][0]["knowledge_id"],"curated:a")
            s.write_text(json.dumps({"projects":[{"name":"lab","findings":[]}]}))
            self.assertEqual(correlate(k,s)["scanner_findings"],0)
if __name__=="__main__":unittest.main()
