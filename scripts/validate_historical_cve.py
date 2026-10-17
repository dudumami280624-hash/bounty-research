#!/usr/bin/env python3
"""Validate the historical CVE manifest and persisted checkpoint files."""
import datetime as dt
import gzip
import json
from pathlib import Path

root = Path("historical-cve")
manifest = json.loads((root / "manifest.json").read_text())
expected = dt.date(1999, 1, 1)
target = dt.date(2026, 10, 14)
seen = set()
errors = []
records_read = 0
for key, info in sorted(manifest.items()):
    begin = dt.datetime.strptime(key[:8], "%Y%m%d").date()
    end = dt.datetime.strptime(key[9:], "%Y%m%d").date()
    if begin != expected:
        errors.append(f"Noncontiguous window: {key}; expected {expected}")
    expected = end
    matches = list(root.rglob(f"*{key}*.gz"))
    if len(matches) != 1:
        errors.append(f"Missing or ambiguous checkpoint {key}: {len(matches)} files")
        continue
    try:
        with gzip.open(matches[0], "rt", encoding="utf-8") as stream:
            payload = stream.read()
        try:
            data = json.loads(payload)
            rows = data if isinstance(data, list) else data.get("vulnerabilities", data.get("records", []))
        except json.JSONDecodeError:
            rows = [json.loads(line) for line in payload.splitlines() if line.strip()]
        if len(rows) != info["count"]:
            errors.append(f"Count mismatch for {key}: {len(rows)} vs {info['count']}")
        for row in rows:
            nested = row.get("cve")
            identifier = nested.get("id") if isinstance(nested, dict) else row.get("id", row.get("cveId"))
            if not identifier or identifier in seen:
                errors.append(f"Missing or duplicate CVE ID: {identifier}")
            seen.add(identifier)
        records_read += len(rows)
    except Exception as exc:
        errors.append(f"Unreadable checkpoint {key}: {exc}")
if expected != target:
    errors.append(f"Incomplete coverage: {expected} versus {target}")
print(json.dumps({"windows": len(manifest), "records_read": records_read, "unique_ids": len(seen), "errors": errors[:50], "error_count": len(errors)}, indent=2))
if errors:
    raise SystemExit(1)
