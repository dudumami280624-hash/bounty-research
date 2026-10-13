#!/usr/bin/env python3
"""Validate Horizen's real deployed contracts on a LOCAL Foundry fork.

Reads only from the public Horizen testnet RPC. No private key, wallet, or --broadcast.
A green result proves deployment assumptions and negative controls, NOT an exploit.
"""
import json
import hashlib
import urllib.request
import urllib.error
import time
import os
import urllib.parse
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
# Public read-only endpoints for the same chain (2651420), never other networks.
RPC_ENDPOINTS=(RPC, "https://horizen-rpc-testnet.appchain.base.org/",
               "https://2651420.rpc.thirdweb.com/",
               "https://explorer-testnet.horizen.io/api/eth-rpc",
               "https://horizen-testnet.explorer.caldera.xyz/api/eth-rpc")
TESTS=(
    "test_RealFork_OfficialContractsHaveRuntimeBytecode",
    "test_RealFork_StakeAndRewardShareActualToken",
    "test_RealFork_UnknownAccountCannotNotifyReward",
    "test_RealFork_RewardWindowCannotBeBypassedEarly",
    "test_RealFork_ActualTokenPrincipalCannotBeStolenViaWithdraw",
    "test_RealFork_ActualTokenTransferDoesNotCallbackReceiver",
    "test_RealFork_ActualTokenApproveDoesNotCallbackSpender",
)


DEPLOYMENTS = {
    "token": "0xb06EC4ce262D8dbDc24Fac87479A49A7DC4cFb87",
    "staker": "0x6BF7CF29a8bcE11Aa62Cf593d165C244fA4d3E31",
    "accumulator": "0x06f5555fee73EDdc385b6d76FE00DB2D96ccDaE8",
}

def rpc_read(method, params, rpc_url=None):
    """Retry only transient failures of public, read-only JSON-RPC calls."""
    if method not in ("eth_chainId", "eth_blockNumber", "eth_getBlockByNumber", "eth_getCode"):
        raise ValueError("RPC method is not read-only allowlisted")
    endpoint = rpc_url or RPC
    request = urllib.request.Request(endpoint,
        data=json.dumps({"jsonrpc":"2.0","id":1,"method":method,"params":params}).encode(),
        headers={"Content-Type":"application/json","Accept":"application/json","User-Agent":"BountyResearchReadOnly/1.0"}, method="POST")
    for attempt in range(3):
        try:
            with urllib.request.urlopen(request, timeout=20) as response:
                value = json.loads(response.read(2_000_000))
            if value.get("error") or "result" not in value:
                raise ValueError("RPC read failed")
            return value["result"]
        except urllib.error.HTTPError as err:
            if err.code not in (429, 500, 502, 503, 504) or attempt == 2:
                raise
        except (urllib.error.URLError, TimeoutError):
            if attempt == 2:
                raise
        time.sleep(0.5 * (attempt + 1))

def deployment_snapshot(read=rpc_read):
    if int(read("eth_chainId", []), 16) != 2651420:
        raise ValueError("Unexpected chain")
    tag = read("eth_blockNumber", [])
    number = int(tag, 16)
    block = read("eth_getBlockByNumber", [tag, False])
    if not isinstance(block, dict) or int(block.get("number", "0x0"),16) != number:
        raise ValueError("Invalid block identity")
    block_hash = block.get("hash")
    if not isinstance(block_hash,str) or len(block_hash)!=66:
        raise ValueError("Missing block hash")
    codes = {}
    for name,address in DEPLOYMENTS.items():
        raw = read("eth_getCode", [address, tag])
        if not isinstance(raw,str) or not raw.startswith("0x"):
            raise ValueError("Invalid runtime bytecode")
        code = bytes.fromhex(raw[2:])
        if not code:
            raise ValueError("Missing deployed runtime bytecode")
        codes[name] = {"address":address,"bytes":len(code),
                       "runtime_sha256":hashlib.sha256(code).hexdigest()}
    return {"fork_block_number":number,"fork_block_hash":block_hash,
            "deployment_code":codes,"deployment_source_match_verified":False}


def diagnose_rpc_methods(endpoint):
    """Identify the exact failing read method, without writing or sending transactions."""
    results=[]
    tag=None
    for method,params in (("eth_chainId",[]),("eth_blockNumber",[])):
        try:
            value=rpc_read(method,params,rpc_url=endpoint)
            results.append({"method":method,"status":"ok"})
            if method=="eth_blockNumber": tag=value
        except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError,ValueError) as err:
            results.append({"method":method,"status":"failed",
                            "http_status":getattr(err,"code",None),
                            "error_type":type(err).__name__})
            return results
    if tag:
        for method,params in [("eth_getBlockByNumber",[tag,False])]+[
            ("eth_getCode",[address,tag]) for address in DEPLOYMENTS.values()]:
            try:
                rpc_read(method,params,rpc_url=endpoint)
                results.append({"method":method,"status":"ok"})
            except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError,ValueError) as err:
                results.append({"method":method,"status":"failed",
                                "http_status":getattr(err,"code",None),
                                "error_type":type(err).__name__})
                break
    return results


def select_rpc_snapshot():
    """Choose one public RPC only after verifying chain, block and all deployed code."""
    failures=[]
    configured=os.environ.get("HORIZEN_TESTNET_RPC_URL","").strip()
    if configured:
        parsed=urllib.parse.urlsplit(configured)
        if parsed.scheme!="https" or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError("Configured RPC must be an HTTPS endpoint without URL credentials")
    endpoints=((configured,) if configured else ()) + tuple(
        endpoint for endpoint in RPC_ENDPOINTS if endpoint != configured)
    for endpoint in endpoints:
        try:
            snapshot=deployment_snapshot(
                lambda method, params: rpc_read(method, params, rpc_url=endpoint))
            return endpoint, snapshot
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError, ValueError) as err:
            status=err.code if isinstance(err, urllib.error.HTTPError) else None
            failures.append({"endpoint":urllib.parse.urlsplit(endpoint).hostname,"error_type":type(err).__name__,
                             "http_status":status,"method_diagnostics":diagnose_rpc_methods(endpoint)})
    raise RuntimeError("No configured/public RPC passed deployment verification: "+json.dumps(failures))

def evaluate_output(returncode,output):
    checked=[s for s in TESTS if ("[PASS] "+s+"(") in output]
    good=(returncode==0 and len(checked)==len(TESTS)
          and f"{len(TESTS)} tests passed" in output and "0 failed" in output)
    return good,checked

def main():
    record={"time_utc":datetime.now(timezone.utc).isoformat(),
        "network":"Horizen Testnet", "chain_id":2651420,
        "rpc_url":RPC,"source_commit":EXPECTED_COMMIT,
        "execution":"not_run","tests_passed":0,"tests_expected":len(TESTS),
        "real_deployment_state_checked":False,"real_world_exploit_verified":False,
        "any_public_chain_transaction_broadcast":False,
        "note":"Local fork validation of genuine deployment; does NOT establish a bug bounty finding"}
    stage="preflight"
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
        stage="deployment_snapshot"
        selected_rpc, snapshot=select_rpc_snapshot()
        record.update(snapshot)
        record["rpc_url"]=urllib.parse.urlsplit(selected_rpc).hostname
        stage="foundry_fork"
        cmd=["forge","test","--match-contract","HorizenDeploymentForkTest",
             "--fork-url",selected_rpc,"--fork-block-number",str(record["fork_block_number"]),"-vv"]
        p=subprocess.run(cmd,cwd=BASE,env=env,stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,text=True,timeout=240,check=False)
        good,checked=evaluate_output(p.returncode,p.stdout)
        stage="fork_block_recheck"
        block=rpc_read("eth_getBlockByNumber", [hex(record["fork_block_number"]),False],
                       rpc_url=selected_rpc)
        if not isinstance(block,dict) or block.get("hash") != record["fork_block_hash"]:
            raise ValueError("Fork block changed during validation")
        record.update({"execution":"passed" if good else "failed",
            "tests_passed":len(checked),"tests_confirmed":checked,
            "returncode":p.returncode,"log_excerpt":p.stdout[-4500:],
            "real_deployment_state_checked":good})
    except subprocess.TimeoutExpired:
        record["execution"]="timeout"
        record["error_stage"]=stage
    except Exception as err:
        record["execution"]="error"
        record["error_type"]=type(err).__name__
        record["error_stage"]=stage
        if isinstance(err, urllib.error.HTTPError):
            record["rpc_http_status"]=err.code
        record["error_detail"]=str(err)[:1600]
    (ROOT/"deployment_fork_results.json").write_text(
        json.dumps(record,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    print("Real deployed Horizen local fork:",record["execution"],
          "tests:",record["tests_passed"],"/",len(TESTS),
          "stage:",record.get("error_stage","completed"),
          "error:",record.get("error_type","none"),
          "rpc_http_status:",record.get("rpc_http_status","n/a"))
    if record["execution"]!="passed":
        raise SystemExit(1)

if __name__=="__main__":
    main()
