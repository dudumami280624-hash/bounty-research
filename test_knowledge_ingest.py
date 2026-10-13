import json
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from knowledge_ingest import ingest

CASE = dict(title="Access control",category="authorization",source_url="https://example.org/a",source_revision="abc123",root_cause="missing owner check",invariant="Only owner may upgrade",detection="Inspect upgrade authorization",remediation="Enforce owner authorization")
class KnowledgeTests(unittest.TestCase):
    def test_repeated_ingestion_preserves_identity(self):
        with TemporaryDirectory() as d:
            src=Path(d)/"cases.json"
            out=Path(d)/"db.json"
            src.write_text(json.dumps([CASE,CASE]))
            first=ingest(src,out)
            self.assertEqual(first["new"],1)
            self.assertEqual(first["duplicates"],1)
            second=ingest(src,out)
            self.assertEqual(second["new"],0)
            self.assertEqual(second["total"],1)
            entry=next(iter(json.loads(out.read_text()).values()))
            self.assertEqual(entry["verification"],"unverified")
    def test_missing_provenance_fails_closed(self):
        with TemporaryDirectory() as d:
            src=Path(d)/"cases.json"
            src.write_text(json.dumps([{"title":"Incomplete"}]))
            with self.assertRaises(ValueError):
                ingest(src,Path(d)/"db.json")
if __name__=="__main__":
    unittest.main()
