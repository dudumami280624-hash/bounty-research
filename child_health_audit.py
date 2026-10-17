"""Read-only GitHub Actions health audit; no paid APIs or external scans."""
import json,os,sys,urllib.request
from datetime import datetime,timezone
from pathlib import Path

OWNER_REPO=os.environ.get("GITHUB_REPOSITORY","dudumami280624-hash/bounty-research")
WORKFLOW="child-shannon-diagnostic.yml"
OUT=Path(os.environ.get("AUDIT_OUTPUT","child-evidence/health-audit.json"))

def api(path):
    req=urllib.request.Request(
        "https://api.github.com/repos/"+OWNER_REPO+"/"+path,
        headers={"Authorization":"Bearer "+os.environ["GITHUB_TOKEN"],
                 "Accept":"application/vnd.github+json",
                 "User-Agent":"child-health-audit"})
    with urllib.request.urlopen(req,timeout=30) as res:
        return json.load(res)

def main():
    runs=api("actions/workflows/"+WORKFLOW+"/runs?per_page=12").get("workflow_runs",[])
    # Do not treat queued or running jobs as completed.
    completed=[r for r in runs if r.get("status")=="completed"]
    latest=completed[0] if completed else None
    report={"checked_at":datetime.now(timezone.utc).isoformat(),
            "workflow":WORKFLOW,"run_id":latest.get("id") if latest else None,
            "run_url":latest.get("html_url") if latest else None,
            "conclusion":latest.get("conclusion") if latest else "no_completed_run",
            "steps":[],"failure_stage":None,"next_action":None,
            "automatic_code_changes":False}
    if latest:
        jobs=api("actions/runs/"+str(latest["id"])+"/jobs?per_page=100").get("jobs",[])
        for job in jobs:
            for step in job.get("steps",[]):
                report["steps"].append({"name":step.get("name"),"conclusion":step.get("conclusion")})
                if step.get("conclusion")=="failure" and not report["failure_stage"]:
                    report["failure_stage"]=step.get("name")
    stage=(report["failure_stage"] or "").lower()
    if stage:
        if "syntax" in stage: action="Inspect Python unit test traceback in job logs; fix regression before downloading models."
        elif "build" in stage: action="Inspect llama.cpp compilation and dependency logs; pin versions if needed."
        elif "download" in stage: action="Verify model URL, SHA256, license, size and network errors."
        elif "diagnosis" in stage: action="Inspect both raw answers and rubric results in uploaded evidence; distinguish model error from infrastructure failure."
        else: action="Inspect the failed step's job logs and preserve a redacted traceback."
        report["next_action"]=action
    elif report["conclusion"]=="success":
        report["next_action"]="Inspect saved original and unseen-case answers; green CI alone is not independent validation."
    else:
        report["next_action"]="No completed run or no failed step found; check run status and jobs."
    OUT.parent.mkdir(parents=True,exist_ok=True)
    OUT.write_text(json.dumps(report,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    summary=os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary,"a",encoding="utf-8") as f:
            f.write("## AI child automated health audit\n\n")
            f.write("Latest completed run: "+str(report["run_url"])+"\n\n")
            f.write("Conclusion: "+str(report["conclusion"])+"\n\n")
            f.write("Failed step: "+str(report["failure_stage"])+"\n\n")
            f.write("Next action: "+report["next_action"]+"\n")
    print(json.dumps({k:report[k] for k in ("run_id","conclusion","failure_stage","next_action")},ensure_ascii=False))
    return 0

if __name__=="__main__":
    try: sys.exit(main())
    except Exception as exc:
        OUT.parent.mkdir(parents=True,exist_ok=True)
        OUT.write_text(json.dumps({"audit_error":type(exc).__name__,"detail":str(exc)[:400]},ensure_ascii=False)+"\n")
        print("Audit failed:",type(exc).__name__,file=sys.stderr)
        sys.exit(1)
