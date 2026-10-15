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
    candidates.sort(key=lambda c: (
        {"direct_scope_candidate": 0, "inherited_requires_impact_proof": 1, "not_proven_in_scope": 2}[c["scope_status"]],
        {"High": 0, "Medium": 1, "Low": 2, "Informational": 3}.get(str(c["impact"]), 4),
        c["candidate_id"],
    ))
    for rank, candidate in enumerate(candidates, 1):
        candidate["review_rank"] = rank
        candidate["poc_gate"] = "blocked_pending_source_and_impact_review"
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
    prioritized = [c for c in result["candidates"] if c["scope_status"] == "direct_scope_candidate"]
    Path("horizen_p0_queue.json").write_text(json.dumps({
        "source": "real_slither_findings",
        "status": "requires_manual_source_and_impact_validation",
        "verified_poc_count": 0,
        "direct_scope_queue": prioritized,
    }, indent=2) + "\n", encoding="utf-8")
    references = {
        "official_known_issues": "https://immunefi.com/bug-bounty/horizen/information/",
        "upstream_security": "https://github.com/HorizenOfficial/staker/blob/main/SECURITY.md",
        "slither_detector_reference": "https://github.com/crytic/slither/wiki/Detector-Documentation",
        "solodit_search": "https://solodit.cyfrin.io/",
        "code4rena_reports": "https://code4rena.com/reports",
    }
    comparisons = []
    for candidate in result["candidates"]:
        comparisons.append({
            "candidate_id": candidate["candidate_id"],
            "detector": candidate["detector"],
            "paths": candidate["paths"],
            "reference_sources": references,
            "comparison_status": "pending_individual_public_report_matching",
            "known_issue_match": "unknown",
            "duplicate_status": "unknown",
            "poc_verified": False,
        })
    Path("horizen_public_crosscheck.json").write_text(json.dumps({
        "scope": "12 real Slither findings; reference index only until individual matching",
        "entries": comparisons,
    }, indent=2) + "\\n", encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k!="candidates"}, indent=2))
