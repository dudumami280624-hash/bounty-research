"""Curated, provenance-aware vulnerability knowledge ingestion (offline, no arbitrary execution)."""
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

REQUIRED = ("title", "category", "source_url", "source_revision", "root_cause", "invariant", "detection", "remediation")

def normalize(item):
    missing = [key for key in REQUIRED if not isinstance(item.get(key), str) or not item[key].strip()]
    if missing:
        raise ValueError("missing knowledge fields: " + ", ".join(missing))
    core = {key: item[key].strip() for key in REQUIRED}
    identity = {key: core[key].lower() for key in ("source_url", "source_revision", "root_cause", "invariant")}
    key = hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()
    return key, core

def ingest(source_file, output_file):
    entries = json.loads(Path(source_file).read_text())
    if not isinstance(entries, list):
        raise ValueError("knowledge source must be a list")
    output = Path(output_file)
    existing = json.loads(output.read_text()) if output.exists() else {}
    inserted = 0
    for entry in entries:
        key, core = normalize(entry)
        if key not in existing:
            existing[key] = {"id": key, **core, "ingested_at_utc": datetime.now(timezone.utc).isoformat(), "verification": "unverified"}
            inserted += 1
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(existing, indent=2, ensure_ascii=False, sort_keys=True) + "\n")
    return {"total": len(existing), "new": inserted, "duplicates": len(entries) - inserted}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("output")
    args = parser.parse_args()
    print(json.dumps(ingest(args.source, args.output)))
