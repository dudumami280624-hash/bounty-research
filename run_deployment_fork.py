#!/usr/bin/env python3
"""Validate Horizen's real deployed contracts on a LOCAL Foundry fork.

Reads only from the public Horizen testnet RPC. No private key, wallet, or --broadcast.
A green result proves deployment assumptions and negative controls, NOT an exploit.
"""
import json
import os
import pathlib
import shutil
import subprocess
from datetime import datetime, timezone

ROOT=pathlib.Path(__file__).resolve().parent
BASE=ROOT/"_work"/"0"
SOURCE=ROOT/"poc"/"HorizenDeploymentFork.t.sol"
TARGET=BASE/"test"/"HorizenDeploymentFork.t.sol"
EXPECTED_COMMIT="ab92502e9da98784dfe3bd3ef933d4e9345ff628"
RPC="https://horizen-testnet.rpc.caldera.xyz/http"
TESTS=(
    "test_RealFork_OfficialContractsHaveRuntimeBytecode",
    "test_RealFork_StakeAndRewardShareActualToken",
    "test_RealFork_UnknownAccountCannotNotifyReward",
    "test_RealFork_RewardWindowCannotBeBypassedEarly",
    "test_RealFork_ActualTokenPrincipalCannotBeStolenViaWithdraw",
)

def evaluate_output(returncode,output):
    checked=[s for s in TESTS if ("[PASS] "+s+"(") in output]
    good=(returncode==0 and len(checked)==len(TESTS)
          and "5 tests passed" in output and "0 failed" in output)
    return good,checked

def main():
    record={"time_utc":datetime.now(timezone.utc).isoformat(),
        "network":"Horizen Testnet", "chain_id":2651420,
        "rpc_url":RPC,"source_commit":EXPECTED_COMMIT,
        "execution":"not_run","tests_passed":0,"tests_expected":len(TESTS),
        "real_deployment_state_checked":False,"real_world_exploit_verified":False,
        "any_public_chain_transaction_broadcast":False,
        "note":"Local fork validation of genuine deployment; does NOT establish a bug bounty finding"}
    try:
        if not BASE.is_dir() or not SOURCE.is_file() or not shutil.which("forge"):
            raise RuntimeError("source checkout / Foundry unavailable")
        actual=subprocess.run(["git","rev-parse","HEAD"],cwd=BASE,
            capture_output=True,text=True,check=True,timeout=15).stdout.strip()
        if actual != EXPECTED_COMMIT:
            raise ValueError("Refuse to test unpinned source revision")
        TARGET.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(SOURCE,TARGET)
        env=os.environ.copy()
        for k in list(env):
            if any(part in k.upper() for part in (
                    "TOKEN","SECRET","PASSWORD","PRIVATE_KEY","API_KEY","MNEMONIC")):
                env.pop(k,None)
        cmd=["forge","test","--match-contract","HorizenDeploymentForkTest",
             "--fork-url",RPC,"-vv"]
        p=subprocess.run(cmd,cwd=BASE,env=env,stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,text=True,timeout=240,check=False)
        good,checked=evaluate_output(p.returncode,p.stdout)
        record.update({"execution":"passed" if good else "failed",
            "tests_passed":len(checked),"tests_confirmed":checked,
            "returncode":p.returncode,"log_excerpt":p.stdout[-4500:],
            "real_deployment_state_checked":good})
    except subprocess.TimeoutExpired:
        record["execution"]="timeout"
    except Exception as err:
        record["execution"]="error"
        record["error_type"]=type(err).__name__
    (ROOT/"deployment_fork_results.json").write_text(
        json.dumps(record,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("Real deployed Horizen local fork:",record["execution"],
          "tests:",record["tests_passed"],"/",len(TESTS))
    if record["execution"]!="passed":
        raise SystemExit(1)

if __name__=="__main__":
    main()
