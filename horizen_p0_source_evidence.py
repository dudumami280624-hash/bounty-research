#!/usr/bin/env python3
"""Extract bounded, auditable source evidence for prioritized real Slither findings."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "_work" / "0"
MAX_LINES = 12

def extract(queue, source=SOURCE):
    result = []
    for item in queue.get("direct_scope_queue", []):
        evidence = []
        for path in item.get("paths", []):
            if path not in ("src/ZenStaker.sol", "src/RewardAccumulator.sol"):
                continue
            target = (source / path).resolve()
            if not target.is_relative_to(source.resolve()) or not target.is_file():
                evidence.append({"path": path, "status": "source_missing"})
                continue
            lines = target.read_text(encoding="utf-8").splitlines()
            locations = item.get("locations", [])
            line_numbers = sorted({n for loc in locations if loc.get("path") == path for n in loc.get("lines", []) if type(n) is int and 0 < n <= len(lines)})
            if not line_numbers:
                evidence.append({"path": path, "status": "line_mapping_missing", "total_lines": len(lines)})
                continue
            for n in line_numbers[:4]:
                lo, hi = max(1, n - 4), min(len(lines), n + 7)
                evidence.append({"path": path, "line": n, "source_excerpt": [{"line": k, "text": lines[k-1]} for k in range(lo, min(hi, lo+MAX_LINES-1)+1)]})
        result.append({"candidate_id": item.get("candidate_id"), "detector": item.get("detector"), "source_evidence": evidence, "poc_verified": False})
    return {"kind": "source_evidence_not_poc", "candidates": result}

if __name__ == "__main__":
    queue = json.loads((ROOT / "horizen_p0_queue.json").read_text(encoding="utf-8"))
    triage = json.loads((ROOT / "horizen_candidate_triage.json").read_text(encoding="utf-8"))
    by_id = {c["candidate_id"]: c for c in triage["candidates"]}
    for candidate in queue["direct_scope_queue"]:
        candidate["locations"] = next((f["locations"] for project in json.loads((ROOT / "slither_results.json").read_text(encoding="utf-8"))["projects"] for f in project["findings"] if f.get("check") == candidate["detector"] and sorted({l.get("path") for l in f.get("locations", []) if isinstance(l, dict) and isinstance(l.get("path"), str)}) == candidate["paths"]), [])
    report = extract(queue)
    (ROOT / "horizen_p0_source_evidence.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"candidates": len(report["candidates"]), "with_line_evidence": sum(any("source_excerpt" in e for e in c["source_evidence"]) for c in report["candidates"])}, indent=2))
