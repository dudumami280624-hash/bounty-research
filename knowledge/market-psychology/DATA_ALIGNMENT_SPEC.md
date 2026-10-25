# Data Alignment Specification v0.1

- Store raw source files unchanged and record SHA-256.
- Use observation date, never retrieval date, for joins.
- Daily series remain daily; monthly and quarterly series are not upsampled without an explicit rule.
- For mixed-frequency tests, aggregate daily market data to month-end or use a declared as-of carry-forward.
- No future-revised value may enter a historical decision; vintage data is required where available.
- Preserve missing values; do not silently forward-fill market prices.
- CPI, unemployment, credit and housing variables use their publication-available date when testing decisions.
- Price tests use close-to-close returns unless the experiment declares another convention.
- Every transformation is recorded in the experiment output manifest.
