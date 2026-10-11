# Bounty research starter

This is a **limited, automated public-source review**, NOT a full AI research agent and NOT proof of a vulnerability.

## Deploy
1. Create a **private** GitHub repository (e.g. `bounty-research`).
2. Upload `audit.py`, `config.json`, and `.github/workflows/audit.yml` preserving folder paths.
3. In GitHub, open **Actions** > **Authorized public-source audit** > **Run workflow**.
4. When completed, open the run > **Artifacts** > `review-...` > `audit.json`.
5. GitHub Actions' cron runs approximately hourly but may be delayed or skipped and does not mean 24/7 continuous execution.

## Limitations
- The example examines a publicly readable pinned repository and flags code patterns for human review; it does not test production systems.
- Findings are **not vulnerabilities** until independently validated. No automatic bounty submission.
- Only add repositories whose source you have permission to review, and verify bounty eligibility/scope independently.
- To integrate an LLM, install a secure API-key secret and carefully extend this workflow; that is **not included** here.
