# Historical CVE validation requirements

Historical knowledge intake is incomplete until every expected time window through 2026-10-13 is present. CI must verify that each referenced compressed file exists, decompresses, matches manifest counts, and has unique CVE IDs across all windows. A green ingestion job alone is not evidence of completion. Independent vulnerability detection and patch regression evidence must be evaluated separately.
