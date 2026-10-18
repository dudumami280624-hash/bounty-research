"""Single safe live FreeLLMAPI probe; credentials only via environment."""
import json,os,sys
from free_llm_router import Provider,route,NoFreeProviderAvailable

def main():
    base=os.getenv("FREELLMAPI_BASE_URL","").rstrip("/")
    key=os.getenv("FREELLMAPI_API_KEY","")
    if not base or not key:
        print(json.dumps({"status":"blocked","reason":"gateway URL or key not configured"}))
        return 2
    if not base.startswith("https://"):
        print(json.dumps({"status":"blocked","reason":"remote gateway must use HTTPS"}))
        return 2
    provider=Provider("freellmapi-cloud-pool",base,os.getenv("FREELLMAPI_MODEL","auto"),"FREELLMAPI_API_KEY")
    try:
        result=route([{"role":"user","content":"Reply with exactly OK"}],[provider],log_path="child-evidence/freellmapi-live.jsonl")
    except NoFreeProviderAvailable:
        print(json.dumps({"status":"blocked","reason":"gateway unavailable; no paid or local fallback"}))
        return 3
    if not result["response"].get("choices"):
        print(json.dumps({"status":"failed","reason":"no completion returned"}))
        return 4
    print(json.dumps({"status":"ok","provider":result["provider"],"usage":result["response"].get("usage",{})}))
    return 0
if __name__=="__main__":sys.exit(main())
