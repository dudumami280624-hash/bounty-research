#!/usr/bin/env python3
"""Fail-closed manifest and persisted CVE checkpoint audit."""
import datetime as dt
import gzip
import json
import re
from pathlib import Path

ROOT = Path("historical-cve")
START = dt.date(1999, 1, 1)
TARGET = dt.date(2026, 10, 14)  # exclusive
errors = []
seen = set()
total = 0
expected = START

def check_window(key, info):
    global expected, total
    match = re.fullmatch(r"(\d{8})-(\d{8})", key)
    if not match:
        errors.append(f"Invalid window key: {key}")
        return
    start, end = (dt.datetime.strptime(s, "%Y%m%d").date() for s in match.groups())
    if start != expected:
        errors.append(f"Gap/overlap: {key}; expected start {expected}")
    if end <= start or end > TARGET or (end - start).days > 119:
        errors.append(f"Invalid window boundaries: {key}")
    if str(info.get("end_exclusive", ""))[:10] != end.isoformat():
        errors.append(f"Manifest end mismatch: {key}")
    expected = end
    paths = list(ROOT.rglob(f"*{key}*.gz"))
    if len(paths) != 1:
        errors.append(f"Expected one persisted gzip for {key}, found {len(paths)}")
        return
    try:
        with gzip.open(paths[0], "rt", encoding="utf-8") as fh:
            body = fh.read()
        try:
            payload = json.loads(body)
            rows = payload if isinstance(payload, list) else payload.get("vulnerabilities", payload.get("records"))
        except json.JSONDecodeError:
            rows = [json.loads(line) for line in body.splitlines() if line.strip()]
        if not isinstance(rows, list):
            raise ValueError("Unrecognized data format")
        if len(rows) != info.get("count"):
            errors.append(f"Count mismatch: {key} actual={len(rows)} manifest={info.get('count')}")
        for row in rows:
            if not isinstance(row, dict):
                errors.append(f"Invalid CVE record in {key}")
                continue
            nested = row.get("cve")
            identifier = nested.get("id") if isinstance(nested, dict) else row.get("id", row.get("cveId"))
            if not isinstance(identifier, str) or not re.fullmatch(r"CVE-\d{4}-\d{4,}", identifier, re.I):
                errors.append(f"Invalid CVE ID in {key}")
                continue
            identifier = identifier.upper()
            if identifier in seen:
                errors.append(f"Duplicate CVE ID: {identifier}")
            seen.add(identifier)
        total += len(rows)
    except Exception as exc:
        errors.append(f"Unreadable checkpoint {key}: {exc}")

try:
    manifest = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError("Manifest must be an object")
    for key, info in sorted(manifest.items()):
        check_window(key, info)
except Exception as exc:
    errors.append(f"Manifest error: {exc}")
    manifest = {}
if expected != TARGET:
    errors.append(f"Incomplete historical coverage: {expected} vs {TARGET}")
print(json.dumps({"windows": len(manifest), "records_read": total, "unique_ids": len(seen), "covered_until_exclusive": str(expected), "target_exclusive": str(TARGET), "error_count": len(errors), "errors": errors[:100]}, indent=2))
raise SystemExit(bool(errors))
