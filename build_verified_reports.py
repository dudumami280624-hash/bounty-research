#!/usr/bin/env python3
"""Generate genuine evidence-backed vulnerability reports, never submit them.

A report can be drafted before the user approves submitting it.
Synthetic callback PoCs cannot satisfy the real-target evidence gate.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT=Path(__file__).resolve().parent
COMMIT="ab92502e9da98784dfe3bd3ef933d4e9345ff628"
REQUIRED=("verified","bounty_scope_verified","known_issue_checked","impact_verified","poc_passed")

def clean_text(value,limit=4000):
    return value.strip()[:limit] if isinstance(value,str) else ""

def read(name,root=ROOT):
    try:
        data=json.loads((root/name).read_text(encoding="utf-8"))
        return data if isinstance(data,dict) else {}
    except (OSError,ValueError):
        return {}

def generate(triage,leads,poc,scope,root=ROOT):
    targets={x.get("id"):x for x in triage.get("findings",[])
             if isinstance(x,dict) and x.get("id")}
    candidates=leads.get("cases",[])
    if not isinstance(candidates,list):candidates=[]
    result={"generated_at_utc":datetime.now(timezone.utc).isoformat(),
            "verified_reports_generated":0,"reports":[],"blocked":[]}
    official=(scope.get("status")=="verified" and scope.get("verified_count")==1
              and scope.get("pinned_commit")==COMMIT)
    real=(poc.get("execution")=="passed" and
          poc.get("real_world_exploit_verified") is True and
          poc.get("conditional_simulation_only") is False and
          poc.get("source_commit")==COMMIT)
    for case in candidates:
        if not isinstance(case,dict):continue
        ident=case.get("id")
        if not isinstance(ident,str) or ident not in targets:continue
        if case.get("verified") is not True:continue
        triaged=targets[ident]
        reason=None
        if not official:reason="official_scope_not_verified"
        elif not real:reason="real_target_poc_not_verified"
        elif triaged.get("commit")!=COMMIT:reason="source_commit_mismatch"
        elif case.get("poc_status")!="finding_specific_poc_passed":reason="no_finding_specific_poc"
        elif any(case.get(k) is not True for k in REQUIRED):reason="missing_security_verification"
        elif not all(clean_text(case.get(k)) for k in (
                "title","security_impact","reproduction_steps","fix_recommendation")):
            reason="missing_report_details"
        path=case.get("evidence_path")
        if reason is None:
            if not isinstance(path,str) or not path.startswith("evidence/") or ".." in path:
                reason="unsafe_evidence_path"
            else:
                base=(root/"evidence").resolve()
                evidence=(root/path).resolve()
                if not evidence.is_relative_to(base) or not evidence.is_file() or evidence.stat().st_size==0:
                    reason="evidence_file_missing_or_empty"
        if reason:
            result["blocked"].append({"id":ident,"reason":reason})
            continue
        text=[
            "# "+clean_text(case["title"],200),
            "",
            "**Project:** Horizen / Immunefi",
            "**Pinned source SHA:** "+COMMIT,
            "**Finding ID:** "+ident,
            "**Affected component:** "+clean_text(triaged.get("description"),450),
            "",
            "## Security impact","",clean_text(case["security_impact"]),"",
            "## Reproduction in an isolated environment","",
            clean_text(case["reproduction_steps"]),"",
            "## Evidence","",str(path),"",
            "## Suggested remediation","",clean_text(case["fix_recommendation"]),"",
            "**Submission:** NOT SENT — separate per-report user approval required.",""
        ]
        destination=root/"reports"/("verified_"+ident+".md")
        destination.parent.mkdir(parents=True,exist_ok=True)
        destination.write_text("\n".join(text),encoding="utf-8")
        result["reports"].append({"id":ident,"path":destination.relative_to(root).as_posix(),
                                  "submitted":False})
    result["verified_reports_generated"]=len(result["reports"])
    return result

def main():
    result=generate(read("triage_results.json"),read("lead_verification.json"),
                    read("specific_poc_results.json"),read("official_scope_status.json"))
    (ROOT/"report_build_status.json").write_text(
        json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Verified report generation:",result["verified_reports_generated"],
          "blocked:",len(result["blocked"]),"never auto-submitted")

if __name__=="__main__":main()
