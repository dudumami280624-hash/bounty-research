#!/usr/bin/env python3
"""Read-only RPC transport diagnostics; no credentials, no bypass, no transactions."""
import json
import os
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime,timezone
from pathlib import Path
from run_deployment_fork import RPC_ENDPOINTS

def probe(endpoint,opener=urllib.request.urlopen):
    hostname=urllib.parse.urlsplit(endpoint).hostname
    req=urllib.request.Request(endpoint,data=b'{"jsonrpc":"2.0","id":1,"method":"eth_chainId","params":[]}',
        headers={"Content-Type":"application/json","Accept":"application/json","User-Agent":"BountyResearchReadOnly/1.0"},method="POST")
    try:
        with opener(req,timeout=12) as res:
            payload=json.loads(res.read(2048))
            chain=payload.get("result")
            return {"host":hostname,"http_status":res.status,"chain_id":chain,
                    "usable":chain=="0x28751c"}
    except urllib.error.HTTPError as e:
        return {"host":hostname,"http_status":e.code,"usable":False,
                "category":"access_denied" if e.code in (401,403) else "http_error"}
    except (urllib.error.URLError,TimeoutError,ValueError,TypeError) as e:
        return {"host":hostname,"usable":False,"category":type(e).__name__}

def main():
    endpoints=list(RPC_ENDPOINTS)
    extra=os.getenv("HORIZEN_TESTNET_RPC_URL","").strip()
    if extra and urllib.parse.urlsplit(extra).scheme=="https":
        endpoints.insert(0,extra)
    result={"time_utc":datetime.now(timezone.utc).isoformat(),
        "expected_chain_id":2651420,"probes":[probe(x) for x in dict.fromkeys(endpoints)]}
    result["rpc_ready"]=any(p["usable"] for p in result["probes"])
    Path("rpc_transport_diagnostics.json").write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result))
if __name__=="__main__":
    main()
