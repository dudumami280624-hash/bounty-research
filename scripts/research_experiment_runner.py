#!/usr/bin/env python3
"""Run the reproducible experiment pipeline.

This runner validates required files, loads the fixed config, and writes a
machine-readable run manifest. Strategy-specific signals are added only after
their definitions are pre-registered in HYPOTHESIS_REGISTER.md.
"""
from __future__ import annotations
import json, hashlib
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "knowledge/market-psychology/HYPOTHESIS_REGISTER.md",
    "knowledge/market-psychology/DATA_ALIGNMENT_SPEC.md",
    "knowledge/market-psychology/BENCHMARKS.md",
    "knowledge/market-psychology/BACKTEST_CONFIG.yaml",
    "knowledge/market-psychology/STATISTICAL_TESTS.py",
    "knowledge/market-psychology/CAUSAL_IDENTIFICATION_REGISTER.md",
    "knowledge/market-psychology/OUT_OF_SAMPLE_REPORT.md",
]

def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    missing = [p for p in REQUIRED if not (ROOT / p).exists()]
    if missing:
        raise SystemExit("Missing required research files: " + ", ".join(missing))
    out = ROOT / "knowledge/market-psychology/experiment-runs"
    out.mkdir(parents=True, exist_ok=True)
    manifest = {
        "run_at_utc": datetime.now(timezone.utc).isoformat(),
        "status": "CONFIG_VALIDATED_DATA_TESTS_PENDING",
        "required_files": {p: sha256(ROOT / p) for p in REQUIRED},
        "data_manifest": str(ROOT / "knowledge/market-psychology/data/us-fred/manifest.json"),
        "next_step": "Implement pre-registered signals and run in-sample, validation, and out-of-sample tests."
    }
    (out / "latest_run.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps(manifest, indent=2))

if __name__ == "__main__":
    main()
