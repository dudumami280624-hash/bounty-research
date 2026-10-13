"""Score detector findings against independent fixture labels.

A finding is positive only when a real scanner reports a reentrancy detector
on the expected fixture. This does not establish exploitability.
"""
import json,sys
from pathlib import Path

def score(report_file, labels_file):
    report=json.loads(Path(report_file).read_text())
    labels=json.loads(Path(labels_file).read_text())
    observations={row["project"]:row for row in report.get("findings",[])}
    tp=fp=tn=fn=0
    for name,expected in labels.items():
        rows=[r for r in report.get("findings",[]) if r.get("project")==name]
        detected=any("reentrancy" in str(r.get("check","")).lower() for r in rows)
        if expected and detected:tp+=1
        elif expected:fn+=1
        elif detected:fp+=1
        else:tn+=1
    return {"tp":tp,"fp":fp,"tn":tn,"fn":fn,"precision":tp/(tp+fp) if tp+fp else None,"recall":tp/(tp+fn) if tp+fn else None,"false_positive_rate":fp/(fp+tn) if fp+tn else None,"scope":"fixture-level reentrancy detection, not exploitable-vulnerability verification"}

if __name__=="__main__":
    result=score(sys.argv[1],sys.argv[2])
    Path(sys.argv[3]).write_text(json.dumps(result,indent=2)+"\n")
    print(json.dumps(result))
    if result["tp"]<1 or result["fp"]>0:raise SystemExit(1)
