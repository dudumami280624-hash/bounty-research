# df03bce1714d — fixed-source static review

Date: 2026-10-12. Source: HorizenOfficial/staker at ab92502e9da98784dfe3bd3ef933d4e9345ff628.
Status: reviewed static lead; NOT a verified vulnerability; NOT ready to submit.

## Attribution
Archived scope_review.py at bounty-research commit 2b790068e1570ba75d92bffdc272f538d3582415 attributes this ID to src/notifiers/TransferFromRewardNotifier.sol. The current raw Slither artifact was not retrieved in this review; this attribution must be cross-checked before closing the lead.

## Code and reachability
TransferFromRewardNotifier._sendTokensToReceiver executes TOKEN.safeTransferFrom(rewardSource, address(RECEIVER), rewardAmount). It is internal. The external entry point is inherited RewardTokenNotifierBase.notify(). Anyone may invoke notify, but the caller supplies no source, destination or amount arguments. The base constructor fixes RECEIVER and TOKEN as immutable fields. rewardSource is initialized in the derived constructor; setRewardSource checks ownership before changing it. Reward amount and interval setters in the base also check ownership. notify rejects early calls and advances nextRewardTime before transfer and receiver notification.

## Conclusion
An arbitrary external caller can trigger a scheduled, configured reward distribution, but this inspected path does not let that caller redirect the receiver or choose an arbitrary approved victim as source. The victim/source must have approved the notifier, and source/amount changes require owner authority. A generic arbitrary-send-erc20 alert therefore does not by itself establish unauthorized theft. No local or live exploit was executed. No blanket claim of contract safety is made (e.g. nonstandard tokens and deployment-specific configuration remain separate questions).

## Evidence gaps and next action
1. Retrieve current raw detector description and structured source mappings to confirm ID attribution.
2. Establish whether this auxiliary notifier is deployed and actually linked to the official in-scope target; do not assume it is an independently eligible asset.
3. If reachable and eligible, run local paired tests proving non-owner configuration changes revert and notification cannot redirect funds. Until then retain unverified/scope-unestablished status.

## Sources
https://github.com/HorizenOfficial/staker/blob/ab92502e9da98784dfe3bd3ef933d4e9345ff628/src/notifiers/TransferFromRewardNotifier.sol
https://github.com/HorizenOfficial/staker/blob/ab92502e9da98784dfe3bd3ef933d4e9345ff628/src/notifiers/RewardTokenNotifierBase.sol
https://github.com/dudumami280624-hash/bounty-research/blob/2b790068e1570ba75d92bffdc272f538d3582415/scope_review.py
