#!/usr/bin/env python3
"""Regression tests for metadata-only MediaCrawler import."""
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).with_name("import_mediacrawler_export.py")
spec = importlib.util.spec_from_file_location("import_mediacrawler_export", SCRIPT)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

class ImportTests(unittest.TestCase):
    def test_duplicate_and_private_fields_not_leaked(self):
        rows = [{"note_id":"123", "title":"K线分析", "user_name":"PRIVATE NAME", "cookies":"SECRET"},
                {"note_id":"123", "title":"K线分析"},
                {"note_id":"456", "desc":"unrelated"}]
        result = mod.summarize(rows, "xhs")
        self.assertEqual(result["total_records"], 3)
        self.assertEqual(result["unique_records"], 2)
        self.assertEqual(result["duplicate_records"], 1)
        self.assertEqual(result["keyword_topic_candidates_unverified"], 1)
        self.assertNotIn("PRIVATE NAME", json.dumps(result))
        self.assertNotIn("SECRET", json.dumps(result))
        self.assertEqual(result["independently_verified_claims"], 0)

    def test_json_and_jsonl_input(self):
        with tempfile.TemporaryDirectory() as tmp:
            for suffix, payload in [(".json", '[{"id":"1"}]'), (".jsonl", '{"id":"1"}\n')]:
                path = Path(tmp) / ("export" + suffix)
                path.write_text(payload, encoding="utf-8")
                self.assertEqual(len(list(mod.load_records(path))), 1)

    def test_unsupported_platform_and_bad_record(self):
        with self.assertRaises(ValueError):
            mod.summarize([], "unsupported")
        result = mod.summarize([{}, {"id":"ok", "url":"javascript:alert(1)"}], "dy")
        self.assertEqual(result["skipped_records"], 2)

if __name__ == "__main__":
    unittest.main()
