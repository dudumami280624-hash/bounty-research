#!/usr/bin/env python3
"""Read-only HackerOne Hacker API connectivity check. Never prints credentials or private reports."""
import base64
import json
import os
import pathlib
import urllib.error
import urllib.request
from datetime import datetime, timezone

OUT = pathlib.Path(__file__).resolve().parent / "hackerone_connection.json"
URL = "https://api.hackerone.com/v1/hackers/me/reports?page%5Bsize%5D=1"

def main():
    result = {
        "time_utc": datetime.now(timezone.utc).isoformat(),
        "service": "HackerOne Hacker API",
        "mode": "READ_ONLY",
        "connected": False,
        "status": "not_checked",
    }
    user = os.getenv("HACKERONE_USERNAME", "").strip()
    token = os.getenv("HACKERONE_API_TOKEN", "").strip()
    if not user or not token:
        result["status"] = "missing_credentials"
        result["missing"] = [name for name, value in
                             (("HACKERONE_USERNAME", user), ("HACKERONE_API_TOKEN", token))
                             if not value]
    else:
        raw = (user + ":" + token).encode("utf-8")
        auth = base64.b64encode(raw).decode("ascii")
        req = urllib.request.Request(URL, headers={
            "Authorization": "Basic " + auth,
            "Accept": "application/json",
            "User-Agent": "BountyResearchReadOnly/1.0",
        }, method="GET")
        try:
            with urllib.request.urlopen(req, timeout=20) as response:
                code = response.status
                payload = json.loads(response.read(262144))
            result["http_status"] = code
            result["connected"] = code == 200 and isinstance(payload.get("data"), list)
            result["status"] = "verified" if result["connected"] else "unexpected_response"
        except urllib.error.HTTPError as err:
            result["http_status"] = err.code
            result["status"] = {401: "auth_failed", 403: "access_forbidden",
                                429: "rate_limited"}.get(err.code, "api_http_error")
        except Exception as err:
            # Never include exception bodies: network libraries may include sensitive URL context.
            result["status"] = "transport_or_parse_error"
            result["error_type"] = type(err).__name__
    OUT.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print("HackerOne read-only check:", result["status"],
          "HTTP:", result.get("http_status", "n/a"))
    if not result["connected"]:
        raise SystemExit(1)

if __name__ == "__main__":
    main()
