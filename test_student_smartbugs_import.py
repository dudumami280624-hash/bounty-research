"""Tests for exact-source, read-only public training corpus ingestion."""
import json
import tempfile
import unittest
from pathlib import Path

from student_smartbugs_import import git_blob_sha1, ingest


class PinnedCorpusTests(unittest.TestCase):
    def test_pinned_blob_import(self):
        content = b"pragma solidity ^0.4.19; contract Example {}\n"
        with tempfile.TemporaryDirectory() as root:
            manifest = Path(root) / "manifest.json"
            output = Path(root) / "corpus.json"
            manifest.write_text(json.dumps({
                "upstream": "https://github.com/smartbugs/smartbugs-curated",
                "upstream_revision": "a" * 40, "license": "Apache-2.0",
                "samples": [{"path": "dataset/reentrancy/test.sol",
                             "blob_sha1": git_blob_sha1(content),
                             "category": "reentrancy", "training_note": "legacy"}]
            }))
            result = ingest(manifest, output, fetch=lambda url: content)
            self.assertEqual(len(result["samples"]), 1)
            self.assertTrue(result["samples"][0]["training_only"])
            self.assertFalse(result["held_out_examples_imported"])

    def test_changed_upstream_blob_fails_closed(self):
        with tempfile.TemporaryDirectory() as root:
            manifest = Path(root) / "manifest.json"
            manifest.write_text(json.dumps({
                "upstream": "pinned", "upstream_revision": "b" * 40, "license": "Apache-2.0",
                "samples": [{"path": "dataset/arithmetic/a.sol", "blob_sha1": "0" * 40,
                             "category": "arithmetic", "training_note": "test"}]
            }))
            with self.assertRaises(ValueError):
                ingest(manifest, Path(root) / "out.json", fetch=lambda url: b"bad source")

    def test_disallows_path_traversal(self):
        with tempfile.TemporaryDirectory() as root:
            manifest = Path(root) / "manifest.json"
            manifest.write_text(json.dumps({
                "upstream": "pinned", "upstream_revision": "b" * 40, "license": "Apache-2.0",
                "samples": [{"path": "dataset/../private.sol", "blob_sha1": "0" * 40,
                             "category": "reentrancy", "training_note": "bad"}]
            }))
            with self.assertRaises(ValueError):
                ingest(manifest, Path(root) / "out.json", fetch=lambda url: b"irrelevant")


if __name__ == "__main__":
    unittest.main()
