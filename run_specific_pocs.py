#!/usr/bin/env python3
"""Run paired local Foundry reproductions against pinned public source (offline)."""
import json,os,pathlib,shutil,subprocess
from datetime import datetime,timezone
ROOT=pathlib.Path(__file__).resolve().parent
base=ROOT/"_work"/"0"
source=ROOT/"poc"/"RewardAccumulatorReentry.t.sol"
target=base/"test"/"RewardAccumulatorReentry.t.sol"
out={"time_utc":datetime.now(timezone.utc).isoformat(),"test_suite":"RewardAccumulatorReentryTest",
     "source_commit":"ab92502e9da98784dfe3bd3ef933d4e9345ff628",
     "execution":"not_run","tests_passed":0,"tests_failed":0,
     "conditional_simulation_only":True,"real_world_exploit_verified":False,
     "official_reward_token_callback_verified":False,"ready_to_submit":False}
try:
    if not base.is_dir() or not source.exists() or not shutil.which("forge"):
        out["execution"]="environment_unavailable"
    else:
        shutil.copyfile(source,target)
        env=os.environ.copy()
        for k in list(env):
            if any(w in k.upper() for w in ("TOKEN","SECRET","PASSWORD","PRIVATE_KEY","API_KEY","RPC_URL","MNEMONIC")):
                env.pop(k,None)
        cmd=["forge","test","--offline","--match-contract","RewardAccumulatorReentryTest","-vv"]
        p=subprocess.run(cmd,cwd=base,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                         text=True,timeout=240,check=False)
        s=p.stdout
        out["execution"]="passed" if p.returncode==0 and "4 tests passed" in s and "0 failed" in s else "failed"
        out["tests_passed"]=4 if out["execution"]=="passed" else 0
        out["returncode"]=p.returncode
        out["log_excerpt"]=s[-1800:]
except subprocess.TimeoutExpired:
    out["execution"]="timeout"
except Exception as error:
    out["execution"]="error"
    out["error_type"]=type(error).__name__
(ROOT/"specific_poc_results.json").write_text(json.dumps(out,indent=2),encoding="utf-8")
print("Conditional local PoC:",out["execution"],"passed:",out["tests_passed"])
if out["execution"]!="passed":raise SystemExit(1)
