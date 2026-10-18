# FreeLLMAPI cloud-only setup (no local model)

FreeLLMAPI is a **router**, not a hosted 7.4B-token API account. Its upstream free providers generally require separate account/API keys; advertised aggregate quotas are not an entitlement. Never commit keys.

## Operator setup

1. Deploy the official FreeLLMAPI router on a machine/server you control, or use its Windows desktop installer. This runs a lightweight router/dashboard, **not a local LLM**. Official docs: https://github.com/tashfeenahmed/freellmapi/blob/main/docs/en/install/01-install.md
2. In its **Keys** dashboard, add free-tier credentials obtained directly from upstream providers, respecting each provider's terms. Disable any paid models or providers and verify free status individually.
3. Copy the router's unified API key from the dashboard. Keep the router private; never expose port 3001 publicly without proper TLS and access controls.
4. For GitHub Actions, a private HTTPS endpoint reachable by the runner is needed. Configure repository Actions secrets `FREELLMAPI_BASE_URL` (ending `/v1`) and `FREELLMAPI_API_KEY`. Do not post them in chat or commit them. If the router stays on localhost, hosted GitHub runners cannot reach it.
5. Run workflow `AI child FreeLLMAPI live cloud probe` manually. It tests a single short chat request and uploads redacted usage evidence. No secrets -> blocked, not green.

The project's runtime supports only cloud free providers; **no Qwen/llama.cpp fallback**. Cloud LLM inference is not the same as running the FreeLLMAPI routing service locally.

## Current status

No authenticated upstream provider or reachable FreeLLMAPI gateway has been supplied. Live requests and automatic 36-provider switching are **not verified**. Only deterministic offline routing tests passed. Do not claim production deployment or 7.4B monthly tokens.
