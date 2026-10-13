"""Bounded, checkpointed historical CVE collection, 1999 through 2026-10-13 UTC."""
import json,time,argparse
from datetime import datetime,timedelta,timezone
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlencode
START=datetime(1999,1,1,tzinfo=timezone.utc)
END=datetime(2026,10,14,tzinfo=timezone.utc)
def collect(out,max_windows=1):
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    manifest=out/"manifest.json"
    state=json.loads(manifest.read_text()) if manifest.exists() else {}
    cursor=START;added=0
    while cursor<END and added<max_windows:
        end=min(cursor+timedelta(days=119),END)
        key=cursor.strftime("%Y%m%d")+"-"+end.strftime("%Y%m%d")
        if key not in state:
            records={};index=0
            while True:
                q=urlencode({"pubStartDate":cursor.strftime("%Y-%m-%dT%H:%M:%S.000"),"pubEndDate":(end-timedelta(milliseconds=1)).strftime("%Y-%m-%dT%H:%M:%S.000"),"resultsPerPage":2000,"startIndex":index})
                req=Request("https://services.nvd.nist.gov/rest/json/cves/2.0?"+q,headers={"User-Agent":"bounty-research-history"})
                for attempt in range(5):
                    try:
                        with urlopen(req,timeout=90) as resp: payload=json.load(resp)
                        break
                    except Exception:
                        if attempt==4: raise
                        time.sleep(10*(attempt+1))
                items=payload["vulnerabilities"]
                for item in items:
                    c=item["cve"];id=c["id"]
                    if c.get("published","")[:10]<="2026-10-13":
                        records[id]={"id":id,"published":c.get("published"),"status":c.get("vulnStatus"),"descriptions":c.get("descriptions"),"weaknesses":c.get("weaknesses"),"references":c.get("references"),"verification":"unverified-locally"}
                index+=len(items)
                if not items or index>=payload["totalResults"]: break
                time.sleep(7)
            (out/(key+".json")).write_text(json.dumps(records,ensure_ascii=False)+"\n")
            state[key]={"count":len(records),"end_exclusive":end.isoformat()}
            manifest.write_text(json.dumps(state,indent=2)+"\n")
            print(key,len(records),flush=True);added+=1
        cursor=end
    print("completed_windows",len(state),"new_windows",added)
if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("--output-dir",default="historical-cve");p.add_argument("--max-windows",type=int,default=1)
    a=p.parse_args();collect(a.output_dir,a.max_windows)
