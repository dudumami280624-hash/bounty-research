#!/usr/bin/env python3
"""Isolated local test baseline for security leads; never certify a vulnerability from static alerts.

Run only pinned, checked-out public source. No RPC, wallet, credentials or external target access.
A passing project's test suite is NOT proof that a specific static alert is exploitable.
"""
import json
import os
import pathlib
import shutil
import subprocess
from datetime import datetime, timezone

ROOT=pathlib.Path(__file__).resolve().parent
config=json.loads((ROOT/"config.json").read_text(encoding="utf-8"))
triage=json.loads((ROOT/"triage_results.json").read_text(encoding="utf-8"))
results=[]
for idx,target in enumerate(config["repositories"]):
    folder=ROOT/"_work"/str(idx)
    record={"project":target["name"],"commit":target["commit"],
            "mode":"isolated_local_forge_test_baseline","test_status":"not_run",
            "reproduced_findings":0,"security_impact_verified":False}
    results.append(record)
    if not folder.is_dir() or not shutil.which("forge"):
        record["test_status"]="environment_unavailable"
        continue
    env=os.environ.copy()
    for key in list(env):
        if any(mark in key.upper() for mark in ("TOKEN","SECRET","PASSWORD","PRIVATE_KEY","API_KEY","RPC_URL","MNEMONIC")):
            env.pop(key,None)
    env["FOUNDRY_DISABLE_NIGHTLY_WARNING"]="1"
    # Explicit offline execution, no live forks or blockchain RPC endpoints.
    cmd=["forge","test","--offline","--fail-fast","--no-match-test","(fork|Fork|FORK)"]
    try:
        p=subprocess.run(cmd,cwd=folder,env=env,stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,text=True,timeout=300,check=False)
        output=p.stdout[-3000:]
        record["test_status"]="passed" if p.returncode==0 and "No tests match" not in output and "0 tests" not in output else "failed_or_incomplete"
        record["returncode"]=p.returncode
        record["log_tail"]=output
    except subprocess.TimeoutExpired:
        record["test_status"]="timeout"
    except OSError as err:
        record["test_status"]="execution_error"
        record["error_type"]=type(err).__name__
for finding in triage.get("findings",[]):
    if finding.get("priority")!="review": continue
    result=next((r for r in results if r["commit"]==finding["commit"]),None)
    finding["reproduction"]="specific_poc_not_run"
    finding["test_baseline"]=result["test_status"] if result else "not_run"
    finding["verified"]=False
    finding["ready_to_submit"]=False
summary={"time_utc":datetime.now(timezone.utc).isoformat(),
         "test_runs":results,
         "leads_checked":sum(f.get("priority")=="review" for f in triage.get("findings",[])),
         "verified_vulnerabilities":0,"ready_to_submit":0,
         "note":"Project baseline testing cannot validate or falsify an individual finding; exploit-specific PoC needed."}
(ROOT/"validation_results.json").write_text(json.dumps(summary,indent=2,ensure_ascii=False),encoding="utf-8")
(ROOT/"triage_results.json").write_text(json.dumps(triage,indent=2,ensure_ascii=False),encoding="utf-8")
print("Isolated validation baseline:",[(x["project"],x["test_status"]) for x in results])
