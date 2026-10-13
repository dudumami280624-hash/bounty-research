"""Fail-closed offline triage; this never authorizes submission."""
REQUIRED = ("pinned_source", "scope_verified", "attacker_control", "reachable",
            "impact_evidence", "reproduction_log", "known_issue_checked",
            "independent_review")
def assess(lead):
    missing = [key for key in REQUIRED if not lead.get(key)]
    if lead.get("synthetic_only") is True:
        missing.append("real_world_conditions")
    return {"candidate_verified": not missing, "missing_evidence": missing,
            "may_submit": False}
