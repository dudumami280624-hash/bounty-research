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
    # Reusable, detector-specific public knowledge; not a fabricated finding match.
    from urllib.parse import quote
    references = {
        "slither_detector_docs": "https://github.com/crytic/slither/wiki/Detector-Documentation",
        "solodit": "https://solodit.cyfrin.io/",
        "code4rena": "https://code4rena.com/reports",
        "horizen_scope": "https://immunefi.com/bug-bounty/horizen/scope/",
        "horizen_information": "https://immunefi.com/bug-bounty/horizen/information/",
    }
    patterns = {
        "reentrancy": {"cause": "External call before relevant state finalization", "test": "Use a local callback contract and assert balance/state invariants across nested calls", "mitigation": "Checks-effects-interactions or suitable reentrancy guard"},
        "unchecked": {"cause": "Ignored return value or failed external interaction", "test": "Use a local callee that fails; assert expected revert or explicit error handling", "mitigation": "Check return values and handle failures"},
        "arbitrary-send": {"cause": "Untrusted destination or authority over token transfer", "test": "Try an unauthorized transfer in a local Foundry test; assert funds cannot move", "mitigation": "Enforce authorization and destination restrictions"},
        "timestamp": {"cause": "Security-sensitive dependence on manipulable block timestamp", "test": "Use vm.warp around boundary conditions; assert invariant holds", "mitigation": "Avoid timestamps for randomness and apply explicit tolerance where appropriate"},
        "delegatecall": {"cause": "Untrusted control over delegatecall target", "test": "Use local malicious target to check storage or authorization invariant", "mitigation": "Restrict trusted implementation addresses"},
        "dos": {"cause": "External revert or unbounded processing prevents intended operation", "test": "Use reverting receiver or bounded workload and verify liveness", "mitigation": "Avoid blocking external calls and bound work"},
    }
    comparisons = []
    for candidate in result["candidates"]:
        detector = str(candidate["detector"] or "").lower()
        pattern = next((v for key, v in patterns.items() if key in detector), None)
        query = quote(detector.replace("-", " ") + " staking smart contract")
        comparisons.append({
            "candidate_id": candidate["candidate_id"],
            "detector": candidate["detector"],
            "paths": candidate["paths"],
            "scope_status": candidate["scope_status"],
            "public_references": references,
            "solodit_search_query": detector.replace("-", " ") + " staking smart contract",
            "github_report_search": "https://github.com/search?q=" + query + "&type=code",
            "reusable_pattern": pattern,
            "comparison_status": "pattern_mapped_not_individually_matched" if pattern else "requires_manual_public_report_matching",
            "known_issue_match": "unknown",
            "duplicate_status": "unknown",
            "poc_verified": False,
            "next_test": pattern["test"] if pattern else "Inspect source mapping and compare public reports before constructing a local test",
        })
    Path("horizen_public_crosscheck.json").write_text(json.dumps({
        "scope": "All 12 Slither candidates; reusable public pattern guidance, not verified duplicates",
        "entries": comparisons,
    }, indent=2) + "\\n", encoding="utf-8")
    print(json.dumps({k:v for k,v in result.items() if k!="candidates"}, indent=2))
