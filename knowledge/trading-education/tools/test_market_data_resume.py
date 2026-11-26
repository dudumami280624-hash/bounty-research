"""Offline regression for batch resume; no market requests."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
import market_data_fetch as m

RAW = b"Date,Open,High,Low,Close,Volume\n2024-01-02,10,12,9,11,100\n"

class ResumeTest(unittest.TestCase):
    def test_reuse_corruption_and_retry(self):
        with tempfile.TemporaryDirectory() as directory:
            out = Path(directory)
            item = {"symbol":"AAA","rows":1,"sha256":hashlib.sha256(RAW).hexdigest(),"source":"fixture","adjustment":"unverified"}
            (out/"AAA.csv").write_bytes(RAW)
            (out/"batch-summary.json").write_text(json.dumps({"results":[item]}))
            with patch.object(m,"fetch",side_effect=ValueError("offline fixture")) as fetch:
                summary = m.run_batch(["AAA","BBB","AAA"],out)
                fetch.assert_called_once_with("BBB",out)
                self.assertEqual(summary["successful"],1)
                self.assertEqual(summary["retry_queue"][0]["symbol"],"BBB")
                self.assertEqual(summary["status"],"partial")
            (out/"AAA.csv").write_bytes(b"corrupt")
            with patch.object(m,"fetch",side_effect=ValueError("offline fixture")) as fetch:
                summary = m.run_batch(["AAA"],out)
                fetch.assert_called_once_with("AAA",out)
                self.assertEqual(summary["status"],"failed")
                self.assertEqual(summary["successful"],0)
            self.assertEqual(json.loads((out/"batch-summary.json").read_text()),summary)

if __name__ == "__main__":
    unittest.main()
