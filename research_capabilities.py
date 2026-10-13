"""Three evidence-gated research capabilities: understanding, transfer, exploration."""
import json
from pathlib import Path

def understanding(case):
    required=("root_cause","invariant","detection","remediation","source_url")
    missing=[k for k in required if not str(case.get(k,"")).strip()]
    return {"ready_for_review":not missing,"missing":missing,"verified":False}

def transfer(labeled_results):
    """Count unique fixture families, not repeated executions."""
    families={}
    for row in labeled_results:
        name=row["family"]
        if name in families:raise ValueError("duplicate fixture family: "+name)
        families[name]=row
    tp=fp=tn=fn=0
    for row in families.values():
        if row["expected"] and row["detected"]:tp+=1
        elif row["expected"]:fn+=1
        elif row["detected"]:fp+=1
        else:tn+=1
    return {"independent_families":len(families),"tp":tp,"fp":fp,"tn":tn,"fn":fn,
            "recall":tp/(tp+fn) if tp+fn else None,
            "false_positive_rate":fp/(fp+tn) if fp+tn else None,
            "transfer_verified":len(families)>=4 and tp>=2 and tn>=2 and fn==0 and fp==0}

def exploration(hypothesis):
    required=("hypothesis","derived_from","independent_fixture","falsification_condition","scanner_evidence","outcome")
    missing=[k for k in required if not hypothesis.get(k)]
    return {"testable":not missing,"missing":missing,"discovery_verified":False}

def evaluate(knowledge_path,labels_path,output_path):
    knowledge=json.loads(Path(knowledge_path).read_text())
    labels=json.loads(Path(labels_path).read_text())
    curated=[v for v in knowledge.values() if v.get("source")=="curated-case"]
    result={"understanding":{"cases":len(curated),"review_ready":sum(understanding(v)["ready_for_review"] for v in curated),"independently_verified":0},
            "transfer":transfer(labels),"exploration":{"hypotheses_tested":0,"discoveries_verified":0}}
    Path(output_path).write_text(json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    return result
if __name__=="__main__":
    import sys
    print(json.dumps(evaluate(*sys.argv[1:4]),ensure_ascii=False))
