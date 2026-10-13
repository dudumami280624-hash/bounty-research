#!/usr/bin/env python3
"""Fail-closed maintenance candidate: deterministic, narrowly scoped repairs only."""
import argparse
import json
from pathlib import Path

def proposal(diagnosis):
    status=diagnosis.get("status")
    if status=="rpc_blocked":
        return {"kind":"rpc_provider_required","change":None,"safe_to_merge":False,
                "reason":"All known RPC endpoints failed; cannot invent an accessible endpoint."}
    if status=="healthy":
        return {"kind":"none","change":None,"safe_to_merge":False}
    return {"kind":"manual_review","change":None,"safe_to_merge":False}

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--diagnosis",default="rpc_maintenance_diagnosis.json")
    p.add_argument("--output",default="repair_proposal.json")
    args=p.parse_args()
    path=Path(args.diagnosis)
    diagnosis=json.loads(path.read_text()) if path.exists() else {"status":"missing_evidence"}
    result=proposal(diagnosis)
    Path(args.output).write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result))
if __name__=="__main__":
    main()
