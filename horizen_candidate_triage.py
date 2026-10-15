#!/usr/bin/env python3
"""Classify real Slither findings by pinned Horizen source scope. Never asserts PoC."""
import json
from pathlib import Path

DIRECT = {"src/ZenStaker.sol", "src/RewardAccumulator.sol"}
INHERITED = {"src/Staker.sol", "src/DelegationSurrogate.sol"}

def classify(report):
    candidates = []
    for project in report.get("projects", []):
        for idx, finding in enumerate(project.get("findings", []), 1):
            paths = sorted({loc.get("path") for loc in finding.get("locations", []) if isinstance(loc, dict) and isinstance(loc.get("path"), str)})
            if DIRECT.intersection(paths):
                status = "direct_scope_candidate"
            elif INHERITED.intersection(paths):
                status = "inherited_requires_impact_proof"
            else:
                status = "not_proven_in_scope"
            candidates.append({
                "candidate_id": f"HORIZEN-{idx:03d}",
                "detector": finding.get("check"),
                "impact": finding.get("impact"),
                "confidence": finding.get("confidence"),
                "paths": paths,
                "scope_status": status,
                "reproducible_poc": False,
                "verified_vulnerability": False,
                "next_action": "Review exact source lines, known issues and construct isolated Foundry test before claiming impact"
            })
    return {
        "analysis": "scope_triage_not_exploit_proof",
        "total_candidates": len(candidates),
        "direct_scope_candidates": sum(c["scope_status"] == "direct_scope_candidate" for c in candidates),
        "verified_vulnerabilities": 0,
        "candidates": candidates
    }

if __name__ == "__main__":
    source = json.loads(Path("slither_results.json").read_text(encoding="utf-8"))
    result = classify(source)
    Path("horizen_candidate_triage.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k!="candidates"}, indent=2))
