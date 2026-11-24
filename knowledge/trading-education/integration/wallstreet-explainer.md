# Wallstreet Explainer — persistent project decision

Upstream: https://github.com/HeyChengC/wallstreet-explainer (MIT code; third-party media excluded).
User authorized integration. Use for original English financial education videos, 16:9 and 9:16, after source and fact review. Keep OCR independent. No paid APIs or automatic publication. Use original charts and authorized media only. Setup entrypoint: tools/setup_wallstreet_explainer.sh. Status: setup script committed; installation/render check not yet verified. Do not count this as textbook research or finished video.

## Entry point clarification
For a persistent external checkout with Python dependencies, use `bash knowledge/trading-education/integration/bootstrap-wallstreet.sh /tmp/wallstreet-explainer` from the repository root. The existing `bash knowledge/trading-education/tools/setup_wallstreet_explainer.sh` is a temporary structural smoke check: it deletes its checkout on exit and does not install Python requirements. Neither script has a verified render result here. See [persistent bootstrap instructions](./WALLSTREET-EXPLAINER.md). Preserve both entry points; do not treat the temporary check as deployment.
