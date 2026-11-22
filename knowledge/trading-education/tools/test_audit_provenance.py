#!/usr/bin/env python3
"""Regression tests for offline source-provenance invariants (synthetic only)."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from audit_provenance import audit

SHA = "a" * 40

def sample():
    return {"topics": {"candlestick": {"status": "needs_independent_fact_check",
        "contradictions_resolved": False, "sources": [{"source_sha": SHA,
        "source_name": "synthetic.pdf", "locations": [{"location": "page-1"}],
        "status": "candidate_unverified"}]}}, "verified_claims": 0}

def main():
    base = sample()
    assert not audit(base)[0], audit(base)
    missing = sample()
    del missing["topics"]["candlestick"]["sources"][0]["source_sha"]
    assert audit(missing)[0], "Missing SHA must fail"
    missing = sample()
    missing["topics"]["candlestick"]["sources"][0]["locations"] = [{"location": ""}]
    assert audit(missing)[0], "Missing page locator must fail"
    invented = sample()
    invented["verified_claims"] = 1
    assert audit(invented)[0], "Unsupported verification must fail"
    invented = sample()
    invented["topics"]["candlestick"]["contradictions_resolved"] = True
    assert audit(invented)[0], "Unsupported contradiction resolution must fail"
    invented = sample()
    invented["topics"]["candlestick"]["sources"][0]["status"] = "verified"
    assert audit(invented)[0], "Source mention must not imply fact verification"
    duplicate = sample()
    duplicate["topics"]["candlestick"]["sources"].append(dict(duplicate["topics"]["candlestick"]["sources"][0]))
    assert audit(duplicate)[1], "Duplicate source should warn"
    print("PASS: 7 synthetic provenance regression scenarios (not fact verification)")

if __name__ == "__main__":
    main()
