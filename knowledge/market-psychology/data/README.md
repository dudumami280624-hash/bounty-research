# Reproducible US Market Data

Run:

python scripts/reproduce_us_market_data.py --start 1920-01-01 --end 2025-12-31

The script downloads public FRED CSV series, stores the raw files, and writes SHA-256 hashes and retrieval metadata to data/us-fred/manifest.json. No chart or numeric claim may be marked reproducible unless it points to a manifest entry.
