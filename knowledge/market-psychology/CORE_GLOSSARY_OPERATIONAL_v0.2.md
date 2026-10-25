# Core Glossary Operational Rules v0.2

These definitions are hypotheses for testing. They are not marked VERIFIED until historical and out-of-sample tests are attached.

## 1. Balance Zone

- Chinese reference: 中枢
- Inputs: rolling high, rolling low, overlapping swing ranges, volume optional
- Timeframe: declared chart timeframe; default monthly for long-history tests
- Recognition: at least three consecutive swings with an overlapping price interval; boundaries are frozen at first identification
- Invalidation: close outside the zone followed by failure to return within the declared confirmation window
- Counterexample: long overlapping ranges that continue without directional resolution
- Theory conflict: comparable to Wyckoff accumulation/distribution and Market Profile value area, but not assumed equivalent; trend following treats it as a potential whipsaw regime
- Test: compare post-break forward returns with random range breaks and buy-and-hold

## 2. Local Turning Pattern

- Chinese reference: 分型
- Inputs: three-bar local high or low
- Timeframe: fixed bar interval
- Recognition: center bar high exceeds adjacent highs, or center bar low is below adjacent lows; no later bars may be used for initial labeling
- Invalidation: subsequent price action removes the turning condition before confirmation
- Counterexample: clustered turns in noisy ranges
- Theory conflict: resembles price-action pivots; efficient-market view treats it as descriptive unless predictive value is shown

## 3. Swing Leg

- Chinese reference: 笔
- Inputs: confirmed local turning patterns and minimum price-distance threshold
- Timeframe: same declared timeframe
- Recognition: connect two confirmed opposite turning patterns only after the minimum distance and confirmation rule are met
- Invalidation: later data changes the earlier pivot under the fixed confirmation rule
- Counterexample: gaps and illiquid prints that create artificial legs
- Theory conflict: similar to Dow swings; trend systems use it as a measurement device, not a standalone signal

## 4. Structural Segment

- Chinese reference: 线段
- Inputs: ordered swing legs, overlap and break conditions
- Timeframe: one declared timeframe with no post-hoc rescaling
- Recognition: segment begins after a confirmed structural break and ends at the first rule-defined termination
- Invalidation: termination rule is triggered or the segment cannot be identified prospectively
- Counterexample: multiple valid decompositions of the same chart
- Theory conflict: conflicts with unique-wave assumptions in Elliott-style readings; must report ambiguity

## 5. Exhaustion Divergence

- Chinese reference: 背驰
- Inputs: price change, momentum measure, volume optional
- Timeframe: fixed lookback and comparison window
- Recognition: price makes a new extreme while the pre-registered momentum measure fails to make a corresponding extreme
- Invalidation: continuation exceeds the pre-registered horizon without reversal or risk reduction
- Counterexample: divergence persists through strong trends
- Theory conflict: momentum literature treats it as possible weakening, not guaranteed reversal; efficient-market status is unresolved

## 6. Decision Zone

- Chinese reference: 买卖点
- Inputs: entry condition, invalidation level, position size, expected holding period
- Timeframe: declared before entry
- Recognition: all four inputs are recorded before the signal is acted upon
- Invalidation: price or thesis condition reaches the pre-registered invalidation
- Counterexample: a technically valid signal with unacceptable liquidity or risk
- Theory conflict: differs from a prediction; risk-defined decision rules can be evaluated against trend and value baselines

## 7. Structural Completion Hypothesis

- Chinese reference: 走势终完美
- Inputs: declared structural sequence and completion criteria
- Timeframe: fixed
- Recognition: only when all criteria are met prospectively; never inferred from the final chart alone
- Invalidation: the sequence extends or resolves without the predicted structural consequence
- Counterexample: trends that remain incomplete for long periods
- Theory conflict: conflicts with efficient-market and open-ended trend models; must remain a falsifiable hypothesis

## 8. Nested Timeframe Analysis

- Chinese reference: 区间套
- Inputs: at least two pre-declared timeframes, aligned signals and conflict rule
- Timeframe: parent/child pair fixed before analysis
- Recognition: higher-timeframe state is evaluated first; lower-timeframe signal is admissible only under the declared parent-state rule
- Invalidation: lower-timeframe signal repeatedly contradicts parent-state rule without risk advantage
- Counterexample: conflicting timeframe signals during regime transitions
- Theory conflict: resembles multi-timeframe trend filters; no equivalence claim without comparative testing

## Verification requirements

Each term needs a reproducible calculation, one US historical case, one failure case, one out-of-sample result and a comparison against Wyckoff, trend following, value and efficient-market interpretations.
