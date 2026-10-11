#!/usr/bin/env python3
"""Turn static detections into deduplicated, evidence-gated report drafts.

No report is automatically labeled verified or sent to a bounty platform.
Only explicitly successful local reproduction evidence may graduate a case.
"""
import hashlib
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "slither_results.json"
OUT = ROOT / "triage_results.json"
DRAFT = ROOT / "report_drafts.md"
SEVERITY = {"High": 0, "Medium": 1, "Low": 2, "Informational": 3, "Optimization": 4}

def triage(data):
    records = []
    seen = set()
    for project in data.get("projects", []):
        for item in project.get("findings", []):
            desc = str(item.get("description", ""))
            check = str(item.get("check") or "unknown")
            impact = str(item.get("impact") or "unknown")
            # Description includes affected source locations; repeat occurrences collapse.
            key = (project.get("commit"), check, desc.strip())
            if key in seen:
                continue
            seen.add(key)
            lower = desc.lower()
            third_party = "lib/" in lower or "node_modules/" in lower or "test/" in lower
            ident = hashlib.sha256(repr(key).encode()).hexdigest()[:12]
            direct = ("src/ZenStaker.sol" in desc or "src/RewardAccumulator.sol" in desc)
            inherited = "src/Staker.sol" in desc and not direct
            scope_relevance = ("direct_in_scope_source" if direct else
                               "inherited_impact_must_be_proven" if inherited else
                               "not_established")
            records.append({
                "id": ident, "project": project.get("name"), "commit": project.get("commit"),
                "scope_relevance":scope_relevance,
                "known_issue_review_required":True,
                "check": check, "impact": impact, "confidence": item.get("confidence"),
                "description": desc[:1800], "third_party_or_test": third_party,
                "priority": "review" if impact in ("High", "Medium") and not third_party else "deferred",
                "reproduction": "not_run", "verified": False,
                "bounty_scope_verified": False, "ready_to_submit": False,
            })
    records.sort(key=lambda x: (SEVERITY.get(x["impact"], 9), x["scope_relevance"]!="direct_in_scope_source", x["third_party_or_test"], x["check"], x["id"]))
    return records

def render(records):
    lines = ["# Automated security triage: UNVERIFIED report drafts", "",
             "Static analyzer alerts are NOT proof of vulnerabilities. No submission or payout is asserted.",
             "Before submission: verify current program scope, reproduce on an isolated local fork,",
             "document impact and include reproducible evidence. Never attack a live target without authorization.", ""]
    for finding in records:
        if finding["priority"] != "review":
            continue
        lines += [
            f'## {finding["id"]}: {finding["check"]} ({finding["impact"]})', "",
            f'- Project: {finding["project"]}', f'- Pinned commit: `{finding["commit"]}`',
            '- Status: UNVERIFIED — not suitable for submission',
            '- Reproduction: not run; impact: unconfirmed; official bounty scope: unverified',
            '- Required: local reproduction, negative control, affected version, demonstrable security impact',
            '', '### Static-analysis lead (not proof)', '',
            '```text', finding["description"][:1200].replace("```", "[code fence]"), '```', ''
        ]
    if not any(x["priority"] == "review" for x in records):
        lines.append("No own-code High/Medium leads met triage thresholds.")
    return "\n".join(lines) + "\n"

def main():
    data = json.loads(SOURCE.read_text(encoding="utf-8"))
    findings = triage(data)
    summary = {"time_utc": datetime.now(timezone.utc).isoformat(),
               "total_alerts": sum(len(x.get("findings", [])) for x in data.get("projects", [])),
               "unique_alerts": len(findings),
               "needs_review": sum(x["priority"] == "review" for x in findings),
               "verified_vulnerabilities": 0, "ready_to_submit": 0,
               "payout_verified_usd": 0,
               "severity_counts": dict(Counter(x["impact"] for x in findings)),
               "findings": findings}
    OUT.write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")
    DRAFT.write_text(render(findings), encoding="utf-8")
    print("Triage:", {k: summary[k] for k in ("total_alerts","unique_alerts","needs_review","verified_vulnerabilities")})

if __name__ == "__main__":
    main()
