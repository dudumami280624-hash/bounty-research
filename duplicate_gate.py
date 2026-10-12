"""Fail-closed public-duplicate and false-positive evidence gate.

Public checks cannot detect private/unpublished reports. No score guarantees.
"""
from datetime import datetime, timezone
import re

def duplicate_gate(case, triaged):
    """Return (allowed, reason). All fields require review-backed evidence."""
    review=case.get("duplicate_review")
    if not isinstance(review,dict):
        return False,"duplicate_review_missing"
    if review.get("decision")!="clear":
        return False,"duplicate_review_not_clear"
    if review.get("same_root_cause_found") is not False:
        return False,"duplicate_root_cause_unresolved"
    if review.get("known_issue_found") is not False:
        return False,"known_issue_unresolved"
    if review.get("independent_reviewer_approved") is not True:
        return False,"independent_review_missing"
    if review.get("source_commit")!=triaged.get("commit"):
        return False,"duplicate_review_commit_mismatch"
    date=review.get("checked_at_utc")
    try:
        checked=datetime.fromisoformat(date.replace("Z","+00:00"))
        if checked.tzinfo is None or checked>datetime.now(timezone.utc):
            return False,"duplicate_review_invalid_date"
        if (datetime.now(timezone.utc)-checked).days>7:
            return False,"duplicate_review_stale"
    except (AttributeError,ValueError,TypeError):
        return False,"duplicate_review_invalid_date"
    sources=review.get("sources_checked")
    required={"official_known_issues","public_disclosures","repository_history","public_audits"}
    if not isinstance(sources,dict) or not required.issubset(sources):
        return False,"duplicate_sources_missing"
    for key in required:
        item=sources[key]
        if not isinstance(item,dict) or item.get("checked") is not True:
            return False,"duplicate_source_not_checked"
        if not isinstance(item.get("evidence"),str) or len(item["evidence"].strip())<12:
            return False,"duplicate_source_evidence_missing"
    fingerprint=review.get("root_cause_fingerprint")
    if not isinstance(fingerprint,str) or not re.fullmatch(r"[a-zA-Z0-9_.:/-]{12,200}",fingerprint):
        return False,"duplicate_fingerprint_missing"
    if review.get("private_reports_visibility")!="unknown":
        return False,"private_report_uncertainty_not_acknowledged"
    return True,"clear_public_checks_only"
