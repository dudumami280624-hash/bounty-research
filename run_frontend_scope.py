#!/usr/bin/env python3
"""Audit the EXACT in-scope Horizen staking frontend from official source.

Uses the frontend's own npm ci, ESLint, TypeScript and Vitest commands.
Dependency advisories are *leads only*, never validated bounty reports.
No wallet secrets, RPC calls, chain writes, or live-site interactions.
"""
import json
import os
import pathlib
import shutil
import subprocess
from datetime import datetime, timezone

ROOT=pathlib.Path(__file__).resolve().parent
URL="https://github.com/HorizenOfficial/staker-services.git"
SHA="a404746a693adca207c8c31f3e21fc3762fbb7b8"
BASE=ROOT/"_frontend_scope"
APP=BASE/"frontend"
OUT=ROOT/"frontend_scope_results.json"

def run(command,cwd,timeout=240,env=None):
    p=subprocess.run(command,cwd=cwd,env=env,stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,text=True,timeout=timeout,check=False)
    return {"ok":p.returncode==0,"code":p.returncode,
            "log_excerpt":p.stdout[-1500:]}

def main():
    result={"time_utc":datetime.now(timezone.utc).isoformat(),
        "source_repo":URL,"source_commit":SHA,"scope":"frontend/",
        "execution":"not_run","source_pinned":False,"checks":{},
        "security_vulnerabilities_verified":0,"bounty_reports_ready":0,
        "note":"Native frontend quality checks and dependency audit; NOT proof of a bounty vulnerability"}
    try:
        if not shutil.which("git") or not shutil.which("npm"):
            raise RuntimeError("git or npm not installed")
        if not BASE.is_dir():
            cloned=run(["git","clone","--quiet","--no-checkout",URL,str(BASE)],ROOT,180)
            if not cloned["ok"]:raise RuntimeError("official frontend source clone failed")
        checkout=run(["git","checkout","--quiet",SHA],BASE,60)
        if not checkout["ok"]:raise RuntimeError("pinned frontend commit unavailable")
        actual=run(["git","rev-parse","HEAD"],BASE,15)
        if not actual["ok"]:
            raise RuntimeError("git source verification failed")
        source_sha=subprocess.check_output(["git","rev-parse","HEAD"],cwd=BASE,text=True,timeout=15).strip()
        if source_sha!=SHA:raise RuntimeError("source commit mismatch")
        result["source_pinned"]=True
        if not (APP/"package-lock.json").is_file():
            raise RuntimeError("no committed lockfile")
        env=os.environ.copy()
        for k in list(env):
            if any(x in k.upper() for x in ("TOKEN","SECRET","PASSWORD","PRIVATE_KEY","MNEMONIC","RPC_URL")):
                env.pop(k,None)
        env["CI"]="true"
        steps=[
            ("install",["npm","ci","--ignore-scripts","--no-fund","--no-audit"],300),
            ("typecheck",["npm","run","typecheck"],150),
            ("lint",["npm","run","lint"],150),
            ("test",["npm","run","test"],180)]
        for name,cmd,timeout in steps:
            item=run(cmd,APP,timeout,env)
            result["checks"][name]=item
            if not item["ok"]:
                result["execution"]="failed_at_"+name
                break
        else:
            result["execution"]="passed"
        if result["checks"].get("install",{}).get("ok"):
            advisory=run(["npm","audit","--omit=dev","--json"],APP,90,env)
            try:
                # npm audit returns 1 when vulnerability advisories exist.
                parsed=json.loads(advisory["log_excerpt"])
                result["dependency_advisory_counts"]=parsed.get("metadata",{}).get("vulnerabilities",{})
                result["dependency_advisories_are_verified_exploits"]=False
            except ValueError:
                result["dependency_advisory_status"]="no_machine_readable_result"
    except subprocess.TimeoutExpired:
        result["execution"]="timeout"
    except Exception as err:
        result["execution"]="error"
        result["error_type"]=type(err).__name__
    OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Official scoped frontend:",result["execution"],"pinned:",result["source_pinned"],
          "checks:",{k:v["ok"] for k,v in result["checks"].items()})
    if result["execution"]!="passed":
        raise SystemExit(1)
if __name__=="__main__":main()
