#!/usr/bin/env python3
"""Conservative, unattended RPC maintenance: propose only, never auto-merge."""
import json
import pathlib
import urllib.parse

ROOT=pathlib.Path(__file__).resolve().parent
RESULT=ROOT/"deployment_fork_results.json"
OUTPUT=ROOT/"rpc_maintenance_diagnosis.json"

def classify(result):
    if result.get("execution")=="passed":
        return {"status":"healthy","action":"none","auto_merge_allowed":False}
    if result.get("error_stage")=="deployment_snapshot":
        return {"status":"rpc_blocked","action":"review_rpc_provider_or_endpoint","auto_merge_allowed":False,
                "details":result.get("error_detail","")[:1200]}
    return {"status":"validation_failed","action":"human_review_required","auto_merge_allowed":False,
            "stage":result.get("error_stage","unknown")}

def main():
    if not RESULT.exists():
        diagnosis={"status":"missing_evidence","action":"human_review_required","auto_merge_allowed":False}
    else:
        diagnosis=classify(json.loads(RESULT.read_text()))
    OUTPUT.write_text(json.dumps(diagnosis,indent=2)+"\n")
    print(json.dumps(diagnosis))
    return 0 if diagnosis["status"]=="healthy" else 0

if __name__=="__main__":
    raise SystemExit(main())
