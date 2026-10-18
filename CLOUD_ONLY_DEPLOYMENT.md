# AI child deployment policy: cloud-only, free-only

## Hard requirements

- Use only explicitly configured, authorized **free cloud LLM endpoints**.
- **No local inference fallback**: do not install, download, invoke, or automatically fall back to Qwen, Ollama, llama.cpp or any local model in the production path.
- Never invoke paid APIs. Unknown pricing is not accepted as free.
- On rate limit, timeout, or provider outage, try another independently authorized free provider. Never bypass an account's quota or access controls.
- When all configured free providers fail, stop and persist progress and sanitized error records. No silent paid or local fallback.
- Record model, provider, token usage if returned, and errors; never log API keys or sensitive source data.
- Security research is restricted to authorized targets and local/offline fixtures; external submissions require user approval.

## Implementation state

`free_llm_router.py` provides a free-only cloud OpenAI-compatible routing foundation and an offline test suite. It does **not** yet connect or verify 36 live providers, does not establish a monthly token entitlement, and is not yet wired into an autonomous audit pipeline.

Historical llama.cpp/Qwen experiment workflows remain as evidence of past tests only; they are not part of the production deployment plan.
