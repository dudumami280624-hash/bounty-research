#!/usr/bin/env python3
"""Run local Foundry reproductions; allow free compiler bootstrap, never chain RPC."""
import json,os,pathlib,shutil,subprocess
from datetime import datetime,timezone
ROOT=pathlib.Path(__file__).resolve().parent
base=ROOT/"_work"/"0"
source=ROOT/"poc"/"RewardAccumulatorReentry.t.sol"
target=base/"test"/"RewardAccumulatorReentry.t.sol"
out={"time_utc":datetime.now(timezone.utc).isoformat(),"test_suite":"RewardAccumulatorReentryTest",
     "source_commit":"ab92502e9da98784dfe3bd3ef933d4e9345ff628",
     "execution":"not_run","tests_passed":0,"tests_failed":0,
     "compiler_bootstrap":"Foundry may download pinned solc 0.8.28; no chain RPC or paid API",
     "conditional_simulation_only":True,"real_world_exploit_verified":False,
     "official_reward_token_callback_verified":False,"ready_to_submit":False}
try:
    if not base.is_dir() or not source.exists() or not shutil.which("forge"):
        out["execution"]="environment_unavailable"
    else:
        pinned=subprocess.run(["git","rev-parse","HEAD"],cwd=base,capture_output=True,text=True,check=True).stdout.strip()
        if pinned != out["source_commit"]:
            raise ValueError("Source commit mismatch: refusing unpinned PoC")
        shutil.copyfile(source,target)
        env=os.environ.copy()
        for k in list(env):
            if any(w in k.upper() for w in ("TOKEN","SECRET","PASSWORD","PRIVATE_KEY","API_KEY","RPC_URL","MNEMONIC")):
                env.pop(k,None)
        cmd=["forge","test","--match-contract","RewardAccumulatorReentryTest","-vv"]
        p=subprocess.run(cmd,cwd=base,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                         text=True,timeout=240,check=False)
        s=p.stdout
        expected=("test_Control_NoCallback_SendsOnlyAccountedAmount",
                  "test_StandardERC20_WithSurplus_StillSendsOnlyAccountedAmount",
                  "test_ConditionalMaliciousERC20_CallbackCausesDuplicateSend",
                  "test_CallbackWithoutSurplus_RevertsAtomically",
                  "testFuzz_DivideBeforeMultiply_PreservesSchedule",
                  "testFuzz_StandardERC20_NeverTransfersUnaccountedSurplus")
        names_ok=all(name in s for name in expected)
        out["named_tests_confirmed"]=names_ok
        out["execution"]="passed" if p.returncode==0 and names_ok and "6 tests passed" in s and "0 failed" in s else "failed"
        out["tests_passed"]=6 if out["execution"]=="passed" else 0
        out["returncode"]=p.returncode
        out["log_excerpt"]=s[-1800:]
        # Separate in-scope, fixed-source hypothesis: user-controlled deposit ID lists.
        summary_source=ROOT/"poc"/"ZenStakerSummaryFuzz.t.sol"
        summary_target=base/"test"/"ZenStakerSummaryFuzz.t.sol"
        shutil.copyfile(summary_source,summary_target)
        summary_cmd=["forge","test","--match-contract","ZenStakerSummaryFuzzTest","--fuzz-runs","128","-vv"]
        q=subprocess.run(summary_cmd,cwd=base,env=env,stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT,text=True,timeout=240,check=False)
        required=("testFuzz_OwnedIdReturnsRealReward",
                  "testFuzz_DuplicateAndForeignIdsDoNotInflateRewards",
                  "test_ForeignOnlyIdsYieldNoUnclaimedRewards",
                  "test_TwoOwnedIdsSumRewards",
                  "test_UnknownIdAndDuplicateAreIgnored")
        summary_ok=(q.returncode==0 and all(n in q.stdout for n in required)
                    and "5 tests passed" in q.stdout and "0 failed" in q.stdout)
        out["zen_summary_fuzz"]={
            "execution":"passed" if summary_ok else "failed",
            "tests_expected":5,"tests_passed":5 if summary_ok else 0,
            "source_commit":pinned,"source_path":"src/ZenStaker.sol",
            "function":"getDepositorFullSummary",
            "test_command":" ".join(summary_cmd),
            "fuzz_runs":128,"log_excerpt":q.stdout[-3500:],
            "real_world_exploit_verified":False,
            "conclusion":"No reward inflation shown" if summary_ok else "Unresolved test failure"}
        if not summary_ok:
            out["execution"]="failed"
except subprocess.TimeoutExpired:
    out["execution"]="timeout"
except Exception as error:
    out["execution"]="error"
    out["error_type"]=type(error).__name__
(ROOT/"specific_poc_results.json").write_text(json.dumps(out,indent=2),encoding="utf-8")
print("Conditional local PoC:",out["execution"],"passed:",out["tests_passed"])
if out["execution"]!="passed":raise SystemExit(1)
