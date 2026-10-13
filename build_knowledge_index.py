"""Bridge public advisories into the research knowledge index without inventing detection rules."""
import json,sys
from pathlib import Path

def bridge(advisories, curated, output):
    source=json.loads(Path(advisories).read_text())
    seeds=json.loads(Path(curated).read_text())
    if not isinstance(source,dict) or not isinstance(seeds,dict):
        raise ValueError("expected advisory and curated knowledge dictionaries")
    index={}
    for key,record in sorted(source.items()):
        if not isinstance(record,dict): continue
        ident=str(record.get("ghsa_id") or record.get("id") or key)
        index["ghsa:"+ident]={"id":ident,"source":"github-reviewed-advisory",
          "title":record.get("summary") or record.get("title") or ident,
          "description":record.get("description") or "",
          "weaknesses":record.get("cwe_ids") or record.get("cwes") or [],
          "verification":"public-advisory-not-locally-validated",
          "detector_ready":False}
    for key,record in sorted(seeds.items()):
        index["curated:"+key]={"id":key,"source":"curated-case",
          "title":record.get("title"),"category":record.get("category"),
          "root_cause":record.get("root_cause"),"invariant":record.get("invariant"),
          "detection":record.get("detection"),"remediation":record.get("remediation"),
          "verification":record.get("verification","unverified"),
          "detector_ready":False}
    Path(output).write_text(json.dumps(index,indent=2,ensure_ascii=False,sort_keys=True)+"\n")
    return {"advisories":len(source),"curated":len(seeds),"indexed":len(index)}
if __name__=="__main__":
    print(json.dumps(bridge(*sys.argv[1:4])))
