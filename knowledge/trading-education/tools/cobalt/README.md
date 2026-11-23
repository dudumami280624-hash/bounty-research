# Cobalt | optional video research service

Source: https://github.com/imputnet/cobalt
Official deployment: https://github.com/imputnet/cobalt/blob/main/docs/run-an-instance.md

**Status: deployment configuration only. No running instance, download, or integration is implied by these files.**

## Start on a Docker-capable host

```sh
cd knowledge/trading-education/tools/cobalt
docker compose config
docker compose up -d
docker compose ps
curl -i http://127.0.0.1:9000/
```

Stop with `docker compose down`. This API binds to the **host loopback only** on port 9000; it is not reachable from the public internet by default. If accessing it remotely, configure a private tunnel or a reverse proxy with TLS and access control, then set `API_URL` to the actual externally reachable URL. Do not put API keys, cookies, or authentication tokens in this public repository.

This is **not** a GitHub Actions service, nor does it automatically download videos or ingest media into the 178-textbook research pipeline. Use only content you are permitted to download and study. Verify availability and supported sites on the deployed instance. Keep original textbooks, published lessons, LOCKED rules, and `main` untouched.
