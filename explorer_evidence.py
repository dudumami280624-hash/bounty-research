#!/usr/bin/env python3
"""Independent read-only Blockscout REST evidence for Horizen testnet.

REST data is NOT a JSON-RPC fork and cannot substitute for seven Foundry tests.
"""
import json
import urllib.request
import urllib.error
from datetime import datetime, timezone
from pathlib import Path

BASE="https://explorer-testnet.horizen.io/api/v2"
DEPLOYMENTS={
 "token":"0xb06EC4ce262D8dbDc24Fac87479A49A7DC4cFb87",
 "staker":"0x6BF7CF29a8bcE11Aa62Cf593d165C244fA4d3E31",
 "accumulator":"0x06f5555fee73EDdc385b6d76FE00DB2D96ccDaE8",
}

def fetch(path):
    request=urllib.request.Request(BASE+path,headers={"Accept":"application/json","User-Agent":"BountyResearchReadOnly/1.0"})
    with urllib.request.urlopen(request,timeout=12) as response:
        return json.loads(response.read(500000))

def inspect(read=fetch):
    out={"source":"blockscout_rest","chain_id_expected":2651420,
         "fork_compatible":False,"seven_fork_tests_passed":0,"verified":False,
         "addresses":{}}
    try:
        stats=read("/stats")
        out["stats_available"]=isinstance(stats,dict) and bool(stats)
        for name,address in DEPLOYMENTS.items():
            item=read("/addresses/"+address)
            if not isinstance(item,dict):
                raise ValueError("Invalid explorer address response")
            returned=str(item.get("hash","")).lower()
            match=returned==address.lower()
            is_contract=bool(item.get("is_contract"))
            out["addresses"][name]={"address_match":match,"is_contract":is_contract}
            if not match or not is_contract:
                raise ValueError("Explorer address is not the expected deployed contract")
        out["verified"]=bool(out["stats_available"]) and len(out["addresses"])==3
        out["status"]="rest_contract_metadata_verified" if out["verified"] else "rest_unverified"
    except (urllib.error.HTTPError,urllib.error.URLError,TimeoutError,ValueError,KeyError,TypeError) as error:
        out["status"]="rest_unavailable"
        out["error_type"]=type(error).__name__
        if isinstance(error,urllib.error.HTTPError):
            out["http_status"]=error.code
    return out

if __name__=="__main__":
    result=inspect()
    result["time_utc"]=datetime.now(timezone.utc).isoformat()
    Path("explorer_evidence.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result))
