"""Six-step offline research cycle with evidence-preserving transitions."""
STEPS = ("collect", "root_cause", "historical_replay",
         "adapt_detector", "authorized_validation", "feedback")
REQUIRED = {
    "collect": ("source_url", "source_type", "license_reviewed"),
    "root_cause": ("affected_component", "root_cause", "security_invariant"),
    "historical_replay": ("vulnerable_revision", "fixed_revision", "replay_log"),
    "adapt_detector": ("detector_path", "positive_fixture", "negative_fixture"),
    "authorized_validation": ("official_scope_url", "scope_verified",
                              "testing_authorized", "pinned_revision", "validation_log"),
    "feedback": ("outcome", "limitations", "next_action"),
}

def evaluate_cycle(record):
    """Never infer verification from a replayed public bug."""
    steps = {}
    for step in STEPS:
        fields = record.get(step, {})
        missing = [key for key in REQUIRED[step] if not fields.get(key)]
        steps[step] = {"complete": not missing, "missing": missing}
    scope = record.get("authorized_validation", {})
    allowed = scope.get("scope_verified") is True and scope.get("testing_authorized") is True
    steps["authorized_validation"]["complete"] &= allowed
    if not allowed:
        steps["authorized_validation"]["missing"].append("explicit_authorization")
    return {
        "steps": steps,
        "engineering_cycle_complete": all(x["complete"] for x in steps.values()),
        "real_world_vulnerability_verified": False,
        "submission_authorized": False,
    }
