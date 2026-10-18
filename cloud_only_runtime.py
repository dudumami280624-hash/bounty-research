"""Cloud-only free-provider runtime. Fails closed without authorized credentials."""
import argparse,json,os
from pathlib import Path
from free_llm_router import load_providers,route,NoFreeProviderAvailable

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--config",default="config/free-cloud-providers.json")
    p.add_argument("--prompt",default="只回答：云端免费模型连接正常。")
    p.add_argument("--evidence",default="child-evidence/cloud-router-usage.jsonl")
    a=p.parse_args()
    providers=load_providers(a.config)
    if not providers:
        print(json.dumps({"status":"blocked","reason":"no authorized free cloud providers configured"}))
        return 2
    try:
        result=route([{"role":"user","content":a.prompt}],providers,log_path=a.evidence)
    except NoFreeProviderAvailable:
        print(json.dumps({"status":"blocked","reason":"all configured free providers unavailable; no local or paid fallback"}))
        return 3
    response=result["response"]
    if not response.get("choices"):
        print(json.dumps({"status":"failed","reason":"provider returned no choices"}))
        return 4
    print(json.dumps({"status":"ok","provider":result["provider"],"model":response.get("model"),
                      "usage":response.get("usage",{})},ensure_ascii=False))
    return 0
if __name__=="__main__":
    raise SystemExit(main())
