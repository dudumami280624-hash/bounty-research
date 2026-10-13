# Authorized target rotation — Intuition V2 (2026-10-13)

Status: research candidate only; no vulnerability verified and no exploit or public-chain transaction performed.

## Official scope and restrictions
- Program: https://immunefi.com/bug-bounty/intuition/scope/
- Scope checked: 2026-10-13 UTC. The program lists the Intuition Mainnet MultiVault proxy as in scope.
- Testing must be local fork only. Mainnet/testnet testing, trusted-admin actions, known audit issues and mempool-ordering/MEV hypotheses are excluded.
- Official codebase: https://github.com/0xIntuition/intuition-contracts-v2
- Pinned source commit for offline review: `94bddae0869f8fbf1cfb4a137aeb78b7fe302fcb` (2026-07-07).
- Deployed proxy-to-implementation correspondence: NOT YET VERIFIED. Do not claim deployed-source proof.

## New hypothesis: duplicate-term batch redemption accounting
- Identifier: INT-MV-20261013-01
- Source: `src/protocol/MultiVault.sol` lines 854-906, `redeemBatch` and `_processRedeem`.
- Attacker-controlled inputs: termIds, curveIds, shares, minAssets for the attacker's own deposits. No trusted privilege assumed.
- Invariant: for identical termId/curveId repeated in one batch, total assets released and final shares/utilization must match an equivalent valid sequence of single redeems, accounting for fees and rounding; no unrelated user balance can be reduced.
- Why investigate: the batch loop updates each vault before removing total utilization once. Existing pinned `tests/unit/MultiVault/RedeemBatch.t.sol` includes ordinary batches, but no explicit duplicate-term case was located in this review.
- Controls: a normal batch of distinct terms; equivalent sequential redemptions; duplicate term with shares exceeding balance must revert atomically.
- Suggested isolated command after adding a test: `forge test --match-test testFuzz_DuplicateTermBatchConservation -vv`.
- Reachability: external function exists; authorization check and nonReentrant modifier present.
- Exploitability: UNKNOWN. No test executed; no accounting violation or real financial impact established.
- Known-issue review: the official program excludes published audit findings. Compare against Consensys Diligence and Code4rena reports before treating any deviation as novel.
- Next step: add a paired Foundry test in a pinned checkout, run locally, compare actual results, and discard if invariant holds.

## Evidence-quality correction pending
The 2026-10-13 deployment fork state has `deployment_source_match_verified=false` despite 7/7 behavior tests passing. `research_scoreboard.py` currently labels this `real_chain_validation=passed`. A local fail-closed patch with five positive/negative tests exists in the prior round's evidence archive, but paired test updates were blocked by the GitHub write safety check. An incomplete source-only change was reverted. Do not count that correction as integrated or verified.

## Metrics (this rotation)
- New officially scoped candidates reviewed: 1/1 (scope page; deployment correspondence not established).
- New hypotheses: 1.
- Foundry hypothesis-specific tests executed: 0/1.
- Verified new bounty vulnerabilities: 0.
- Official submissions: 0.
- New paid services: 0.
