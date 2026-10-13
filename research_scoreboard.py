#!/usr/bin/env python3
"""Evidence-separated acceptance: green CI never means verified exploit or bounty."""
import json
from pathlib import Path

def load(path):
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return None

def scoreboard(fork, submission, acceptance):
    fork=fork or {}
    submission=submission or {}
    acceptance=acceptance or {}
    passed=fork.get("execution")=="passed" and fork.get("tests_passed")==7
    source_matched=fork.get("deployment_source_match_verified") is True
    return {
        "workflow_execution": "independent_ci_result",
        "real_chain_validation": ("passed" if passed and source_matched else
                                  "behavior_observed_source_unverified" if passed else
                                  "blocked" if fork.get("error_stage")=="deployment_snapshot" else "unverified"),
        "deployment_source_correspondence": "verified" if source_matched else "unverified",
        "real_chain_tests_passed": 7 if passed else 0,
        "verified_vulnerability": "unverified",
        "official_bounty_payment": "unverified",
        "submission_evidence_present": bool(submission),
        "acceptance_evidence_present": bool(acceptance),
        "no_automatic_claims": True
    }

if __name__=="__main__":
    result=scoreboard(load("deployment_fork_results.json"),load("submission_status.json"),load("acceptance_status.json"))
    Path("research_scoreboard.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result))
