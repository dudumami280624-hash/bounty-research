# Scrapling -> bounty-research integration boundary

Scrapling is an **intake-only** component. An operator may supply an HTML snapshot of a publicly accessible official bounty page and its exact URL to `bounty_intake.py`. The resulting JSON is a **candidate lead**, not an eligibility approval, security finding, report, or payout.

The existing `audit.yml`, `verify_official_scope.py`, `build_verified_reports.py`, and submission gates remain unchanged. No live scraping, automatic submission, credential handling, evasion, or production-target testing is enabled.

Manual example after installing requirements:
`python tools/scrapling/bounty_intake.py --html snapshot.html --source-url https://example.org/bounty --output lead.json`

GitHub Actions workflow `scrapling-bounty-intake.yml` runs **offline tests only** on demand. Actual workflow success and upstream dependency installation are not yet verified.
