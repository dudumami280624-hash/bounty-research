"""Deterministic, fail-closed research path selection; no target is auto-authorized."""
from datetime import datetime, timezone

CHANNELS = ("contract", "web_api", "patch_diff", "variant", "tooling")
BLOCKED = {"blocked", "disproved", "duplicate"}
REQUIRED = ("id", "channel", "scope_verified", "authorization_verified", "evidence", "last_updated")


def eligible(path):
    if not isinstance(path, dict) or any(k not in path for k in REQUIRED):
        return False
    if path["channel"] not in CHANNELS or path["scope_verified"] is not True:
        return False
    if path["authorization_verified"] is not True:
        return False
    if not isinstance(path["evidence"], list) or not path["evidence"]:
        return False
    if path.get("status") in BLOCKED or path.get("stale_cycles", 0) >= 2:
        return False
    return isinstance(path.get("priority", 0), (int, float)) and not isinstance(path.get("priority", 0), bool)


def select_path(paths):
    """Returns best authorized path, or None. No network operations or submissions."""
    candidates = [p for p in paths if eligible(p)]
    return sorted(candidates, key=lambda p: (-p.get("priority", 0), p["id"]))[0] if candidates else None


def transition(path, new_evidence=False, source_changed=False):
    """Pause stagnant paths; revive only on independently documented new evidence."""
    result = dict(path)
    if source_changed or new_evidence:
        if not result.get("evidence"):
            raise ValueError("Evidence reference required before reopening")
        result["stale_cycles"] = 0
        if result.get("status") == "blocked":
            result["status"] = "review"
    else:
        result["stale_cycles"] = max(0, result.get("stale_cycles", 0)) + 1
        if result["stale_cycles"] >= 2:
            result["status"] = "blocked"
    result["last_updated"] = datetime.now(timezone.utc).isoformat()
    return result
