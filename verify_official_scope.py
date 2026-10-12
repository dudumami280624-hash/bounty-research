#!/usr/bin/env python3
"""Read-only verification of an exact official Immunefi bounty scope.

Never considers third-party directory listings authorization. Fails closed.
"""
import json
import html
import re
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent
EXPECTED_INFO = "https://immunefi.com/bug-bounty/horizen/information/"
EXPECTED_SCOPE = "https://immunefi.com/bug-bounty/horizen/scope/"
PINNED_SHA = "ab92502e9da98784dfe3bd3ef933d4e9345ff628"

def validate_pages(evidence, information, scope):
    if evidence.get("information_url") != EXPECTED_INFO or evidence.get("scope_url") != EXPECTED_SCOPE:
        return False, "unexpected official page URL"
    if evidence.get("pinned_commit") != PINNED_SHA:
        return False, "pinned source mismatch"
    if set(evidence.get("direct_source_assets") or []) != {
        "src/ZenStaker.sol", "src/RewardAccumulator.sol"
    }:
        return False, "in-scope source assets mismatch"
    # Match official program identity, cash reward, active submission UI,
    # listed target source commit and both contract names.
    # Strip actual HTML tags and decode entities; JSX/HTML splits visible labels.
    inf = re.sub(r"\\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", information))).lower()
    sco = re.sub(r"\\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", scope))).lower()
    information_ok = all(term in inf for term in (
        "horizen", "maximum bounty", "10,000", "submit a bug",
        "runnable poc required", "rewards", "usdc"))
    scope_ok = all(term in sco for term in (
        "horizen", "zenstaker", "rewardaccumulator", "ab92502",
        "submit a bug", "assets in scope"))
    return information_ok and scope_ok, (
        "official scope, cash bounty and submit page validated"
        if information_ok and scope_ok else
        "official markers missing: information=" + ",".join(term for term in (
        "horizen", "maximum bounty", "10,000", "submit a bug", "runnable poc required", "rewards", "usdc")
        if term not in inf) + " scope=" + ",".join(term for term in (
        "horizen", "zenstaker", "rewardaccumulator", "ab92502", "submit a bug", "assets in scope")
        if term not in sco))

def get(url):
    if url not in (EXPECTED_INFO, EXPECTED_SCOPE):
        raise ValueError("non-allowlisted scope URL")
    request=urllib.request.Request(url,headers={
        "User-Agent":"Mozilla/5.0 (compatible; BountyScopeVerification/1.0)",
        "Accept":"text/html,application/xhtml+xml"})
    with urllib.request.urlopen(request,timeout=20) as response:
        final=urlsplit(response.geturl())
        if final.scheme!="https" or final.hostname!="immunefi.com":
            raise ValueError("official scope request redirected outside Immunefi")
        raw=response.read(2_000_001)
        if len(raw)>2_000_000:
            raise ValueError("official scope HTML too large")
        return raw.decode("utf-8","replace")

def main():
    evidence=json.loads((ROOT/"official_scope_evidence.json").read_text(encoding="utf-8"))
    status={"verified_at_utc":datetime.now(timezone.utc).isoformat(),
            "source":"official live pages; not an unofficial candidate directory",
            "program":"Horizen","scope_url":EXPECTED_SCOPE,
            "pinned_commit":PINNED_SHA,
            "verified_count":0,"status":"unverified","reason":"no live verification",
            "live_testing_permitted":False,"local_source_review_only":True}
    try:
        valid,reason=validate_pages(evidence,get(EXPECTED_INFO),get(EXPECTED_SCOPE))
        if valid:
            status.update({"verified_count":1,"status":"verified","reason":reason})
        else:
            status["reason"]=reason
    except Exception as exc:
        status["reason"]="official page not verified: "+type(exc).__name__
    (ROOT/"official_scope_status.json").write_text(
        json.dumps(status,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print("Official scope:",status["status"],"verified:",status["verified_count"],
          "reason:",status["reason"])
    # Do not stop other stages: transparent FAIL through acceptance report.

if __name__=="__main__":
    main()
