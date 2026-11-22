#!/usr/bin/env python3
"""Offline provenance audit for The Market Mind catalog.

Inspired by claude-wiki's source-tag and invariant checks, without Claude API.
This checks reference integrity only; it does NOT verify factual claims.
"""
import argparse
import json
import sys
from pathlib import Path


def audit(catalog):
    errors = []
    warnings = []
    topics = catalog.get("topics")
    if not isinstance(topics, dict):
        return ["topics must be an object"], []
    for topic, record in topics.items():
        if not isinstance(record, dict):
            errors.append(f"{topic}: topic record must be an object")
            continue
        seen = set()
        for index, source in enumerate(record.get("sources", [])):
            prefix = f"{topic}.sources[{index}]"
            if not isinstance(source, dict):
                errors.append(f"{prefix}: expected object")
                continue
            sha = source.get("source_sha")
            if not isinstance(sha, str) or len(sha) < 16 or any(c not in "0123456789abcdef" for c in sha.lower()):
                errors.append(f"{prefix}: missing or malformed source_sha")
            if not source.get("source_name"):
                errors.append(f"{prefix}: missing source_name")
            if sha in seen:
                warnings.append(f"{prefix}: duplicate source SHA within topic")
            seen.add(sha)
            locations = source.get("locations", [])
            if not isinstance(locations, list) or not locations:
                warnings.append(f"{prefix}: no traceable locations")
            else:
                for j, loc in enumerate(locations):
                    if not isinstance(loc, dict) or not isinstance(loc.get("location"), str) or not loc["location"].strip():
                        errors.append(f"{prefix}.locations[{j}]: missing locator")
            if source.get("status") in ("verified", "fact_checked"):
                errors.append(f"{prefix}: source index cannot assert verification")
        if record.get("contradictions_resolved") is True and not record.get("review_evidence"):
            errors.append(f"{topic}: contradiction resolution lacks review evidence")
        if record.get("status") in ("verified", "fact_checked") and not record.get("review_evidence"):
            errors.append(f"{topic}: verified status lacks review evidence")
    if catalog.get("verified_claims", 0) and not catalog.get("verification_evidence"):
        errors.append("nonzero verified_claims without verification_evidence")
    return errors, warnings


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("catalog", type=Path)
    args = parser.parse_args()
    data = json.loads(args.catalog.read_text(encoding="utf-8"))
    errors, warnings = audit(data)
    print(json.dumps({"topics_checked": len(data.get("topics", {})), "errors": errors, "warnings": warnings,
                      "result": "fail" if errors else "pass", "scope": "reference_integrity_only_not_fact_verification"},
                     ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
