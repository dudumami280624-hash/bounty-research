"""Fail-closed local validation of a recorded official scope check.

No network calls. A check record is a human attestation, not official proof.
"""
from datetime import datetime, timezone


def scope_check_is_current(record, *, now=None, max_age_seconds=86400):
    if not isinstance(record, dict) or record.get('status') != 'verified':
        return False
    if record.get('cash_bounty_verified') is not True:
        return False
    if not isinstance(record.get('official_scope_url'), str) or not record['official_scope_url'].startswith('https://'):
        return False
    checked_at = record.get('verified_at_utc')
    if not isinstance(checked_at, str):
        return False
    try:
        checked = datetime.fromisoformat(checked_at.replace('Z', '+00:00'))
        if checked.tzinfo is None:
            return False
        seconds = ((now or datetime.now(timezone.utc)) - checked).total_seconds()
        return -300 <= seconds <= max_age_seconds
    except (TypeError, ValueError, OverflowError):
        return False
