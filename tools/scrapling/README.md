# Scrapling (cloud-only, isolated)

This folder sets up the Scrapling Python dependency for a manually triggered GitHub Actions smoke test. It does **not** scrape external websites, bypass access controls, run on a schedule, or change existing bounty workflows.

GitHub Actions > **Scrapling isolated smoke test** > **Run workflow** installs the dependency on an ephemeral GitHub runner and parses a local HTML string. The workflow is not considered tested until an actual run succeeds.

Any later data collection requires a specific permitted target, scope, rate limits and output design. Never treat scraped material as verified vulnerability evidence.
