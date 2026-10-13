"""Evidence metrics: never invent values when denominator is zero."""
def ratio(numerator, denominator):
    if denominator is None or denominator <= 0:
        return None
    if numerator < 0 or numerator > denominator:
        raise ValueError("invalid metric counts")
    return numerator / denominator

def summarize(counts):
    metrics = {
        "target_coverage": ("eligible_targets", "evaluated_targets"),
        "deep_investigation_completion": ("investigated_leads", "opened_leads"),
        "reproduction_rate": ("reproduced_leads", "investigated_leads"),
        "confirmed_finding_rate": ("verified_findings", "investigated_leads"),
        "false_positive_rate": ("disproved_leads", "investigated_leads"),
        "public_duplicate_prevention": ("public_duplicates_blocked", "public_duplicates_encountered"),
        "report_acceptance": ("accepted_reports", "decided_reports"),
    }
    result = {name: ratio(counts.get(a, 0), counts.get(b, 0))
              for name, (a, b) in metrics.items()}
    hours = counts.get("research_hours", 0)
    result["verified_bounty_usd_per_hour"] = (
        counts.get("confirmed_payout_usd", 0) / hours if hours > 0 else None)
    return result
