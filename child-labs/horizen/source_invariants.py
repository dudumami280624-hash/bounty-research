#!/usr/bin/env python3
"""Static preflight checks of exact pinned source, not a proof of exploitability."""
import json
import sys
from pathlib import Path

source = Path(sys.argv[1]).read_text(encoding="utf-8")
checks = {
    "nonzero_window_guard": "if(_timeWindow == 0)" in source,
    "maximum_window_guard": "if (_timeWindow > MAX_TIME_WINDOW)" in source,
    "whitelist_guard_for_incoming_rewards": "function transferAndNotifyRewards(uint256 amount) external onlyWhitelisted" in source,
    "reward_schedule_grid_alignment": "lastRewardTime += elapsedWindows * timeWindow;" in source,
    "reward_accounting_reset_after_notify": "staker.notifyRewardAmount(rewardAmount);" in source and "accumulatedRewards = 0;" in source,
}
print(json.dumps({"type": "source_pattern_preflight_not_exploit_validation", "checks": checks, "all_patterns_found": all(checks.values())}, indent=2))
if not all(checks.values()):
    sys.exit(1)
