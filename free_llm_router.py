"""Zero-cost OpenAI-compatible multi-provider router. Stdlib only.

Only explicitly allowlisted endpoints are eligible. Never retries a 401/403,
never bypasses quotas; a 429 only switches to another authorized provider.
"""
import json, os, time, urllib.error, urllib.request
from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)
class Provider:
    name: str
    base_url: str
    model: str
    api_key_env: str
    free_only: bool = True

class NoFreeProviderAvailable(RuntimeError):
    pass

def load_providers(config_path: str) -> list[Provider]:
    with open(config_path, encoding="utf-8") as handle:
        config=json.load(handle)
    providers=[]
    for item in config.get("providers", []):
        p=Provider(**item)
        if not p.free_only:
            raise ValueError("Paid provider prohibited: "+p.name)
        if not p.base_url.startswith(("https://","http://127.0.0.1:","http://localhost:")):
            raise ValueError("Unsafe endpoint: "+p.name)
        if not p.model or not p.api_key_env:
            raise ValueError("Missing model or key variable")
        providers.append(p)
    return providers

def request_provider(provider: Provider, messages: list[dict], *, timeout: int=15) -> dict:
    key=os.environ.get(provider.api_key_env,"")
    if not key:
        raise ValueError("Provider not configured: "+provider.name)
    url=provider.base_url.rstrip("/")+"/chat/completions"
    body=json.dumps({"model":provider.model,"messages":messages,"temperature":0}).encode()
    req=urllib.request.Request(url,data=body,headers={
        "Authorization":"Bearer "+key,"Content-Type":"application/json",
        "User-Agent":"bounty-research-free-router/1"},method="POST")
    with urllib.request.urlopen(req,timeout=timeout) as response:
        return json.load(response)

def route(messages: list[dict], providers: list[Provider], *,
          transport: Callable=request_provider, log_path: str="child-evidence/free-router.jsonl") -> dict:
    errors=[]
    for p in providers:
        if not os.environ.get(p.api_key_env):
            errors.append({"provider":p.name,"status":"not_configured"})
            continue
        try:
            result=transport(p,messages)
            if not result.get("choices"):
                errors.append({"provider":p.name,"status":"empty_response"})
                _append(log_path,{"provider":p.name,"status":"empty_response"})
                continue
            usage=result.get("usage",{})
            record={"provider":p.name,"status":"ok","model":p.model,
                    "prompt_tokens":usage.get("prompt_tokens"),"completion_tokens":usage.get("completion_tokens")}
            _append(log_path,record)
            return {"provider":p.name,"response":result}
        except urllib.error.HTTPError as exc:
            status=exc.code
            errors.append({"provider":p.name,"status":status})
            _append(log_path,{"provider":p.name,"status":status})
            if status in (401,403):
                continue  # credentials/permission issue: never retry this provider
            if status not in (408,429,500,502,503,504):
                continue
        except (TimeoutError, urllib.error.URLError, ConnectionError) as exc:
            errors.append({"provider":p.name,"status":type(exc).__name__})
            _append(log_path,{"provider":p.name,"status":type(exc).__name__})
    raise NoFreeProviderAvailable(json.dumps(errors))

def _append(path: str, record: dict) -> None:
    os.makedirs(os.path.dirname(path) or ".",exist_ok=True)
    with open(path,"a",encoding="utf-8") as handle:
        handle.write(json.dumps(record,ensure_ascii=False)+"\n")
