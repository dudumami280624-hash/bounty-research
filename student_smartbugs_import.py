"""Download and cryptographically verify pinned public SmartBugs training examples.

Only explicitly allowlisted upstream files are fetched. Content is evidence/data,
not trusted instructions. No source from this importer is used for blind assessment.
"""
import argparse
import hashlib
import json
from pathlib import Path
from urllib.request import urlopen

BASE = "https://raw.githubusercontent.com/smartbugs/smartbugs-curated"
MAX_SOURCE = 120_000


def git_blob_sha1(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\x00" + data).hexdigest()


def ingest(manifest_path, output, fetch=None):
    manifest = json.loads(Path(manifest_path).read_text(encoding="utf-8"))
    revision = manifest["upstream_revision"]
    if len(revision) != 40 or any(ch not in "0123456789abcdef" for ch in revision):
        raise ValueError("Only pinned hexadecimal upstream commits are supported")
    fetch = fetch or (lambda url: urlopen(url, timeout=30).read(MAX_SOURCE + 1))
    entries = []
    for case in manifest["samples"]:
        path = case["path"]
        if not path.startswith("dataset/") or not path.endswith(".sol") or ".." in path.split("/"):
            raise ValueError("Disallowed source path")
        url = BASE + "/" + revision + "/" + path
        content = fetch(url)
        if len(content) > MAX_SOURCE:
            raise ValueError("Source exceeds safe import limit")
        if git_blob_sha1(content) != case["blob_sha1"]:
            raise ValueError("Upstream training source does not match pinned Git blob")
        text = content.decode("utf-8")
        entries.append({"category": case["category"], "upstream": url,
                        "blob_sha1": case["blob_sha1"],
                        "sha256": hashlib.sha256(content).hexdigest(),
                        "training_note": case["training_note"],
                        "source_excerpt": text[:1200],
                        "training_only": True, "validated_by": "pinned-git-blob"})
    record = {"source": manifest["upstream"], "revision": revision,
              "license": manifest["license"], "samples": entries,
              "held_out_examples_imported": False}
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return record


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", default="knowledge_sources/smartbugs_selected.json")
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    result = ingest(args.manifest, args.output)
    print("Pinned public SmartBugs samples verified:", len(result["samples"]))
