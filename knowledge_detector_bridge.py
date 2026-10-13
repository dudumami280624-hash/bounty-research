"""Consume curated knowledge and static-analysis results for reproducible triage.

Knowledge is used to prioritize and explain independently emitted findings;
it never creates a finding without scanner evidence.
"""
import argparse,json,re
from pathlib import Path

def tokens(value):
    return set(re.findall(r"[a-z][a-z0-9_-]{3,}",str(value).lower()))

def correlate(index,scan):
    entries=json.loads(Path(index).read_text())
    result=json.loads(Path(scan).read_text())
    reports=[]
    for project in result.get("projects",[]):
        for finding in project.get("findings",[]):
            check=str(finding.get("check") or "")
            desc=str(finding.get("description") or "")
            evidence=tokens(check+" "+desc)
            matches=[]
            for key,entry in entries.items():
                if entry.get("source")!="curated-case":continue
                vocabulary=tokens(" ".join(str(entry.get(field) or "") for field in ("category","root_cause","invariant","detection")))
                overlap=sorted(evidence & vocabulary)
                if overlap:
                    matches.append({"knowledge_id":key,"overlap":overlap[:12],"source":entry["source"],"verification":entry.get("verification")})
            matches.sort(key=lambda m:(-len(m["overlap"]),m["knowledge_id"]))
            reports.append({"project":project.get("name"),"check":check,"impact":finding.get("impact"),"locations":finding.get("locations",[]),"knowledge_matches":matches[:5],"status":"unverified-static-triage"})
    return {"scanner_findings":len(reports),"correlated_findings":sum(bool(x["knowledge_matches"]) for x in reports),"findings":reports}

def main():
    p=argparse.ArgumentParser();p.add_argument("knowledge_index");p.add_argument("scanner_results");p.add_argument("output");a=p.parse_args()
    report=correlate(a.knowledge_index,a.scanner_results)
    Path(a.output).write_text(json.dumps(report,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps({"scanner_findings":report["scanner_findings"],"correlated_findings":report["correlated_findings"]}))
if __name__=="__main__":main()
