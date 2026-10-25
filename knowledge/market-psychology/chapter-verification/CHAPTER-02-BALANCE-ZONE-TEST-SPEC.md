# Chapter 02 Empirical Test Specification v0.1

## Claim

A narrow balance range may precede directional repricing, but range breaks can also fail.

## Operational proxy

- Data: Shiller S&P Composite monthly price.
- Lookback: 12 months.
- Balance Zone: prior 12-month high-low width is below the 30th percentile of all rolling widths available before the signal.
- Breakout: current close exceeds the prior 12-month high.
- Outcome: forward 6-month return.
- Benchmark: all months with a breakout above the prior 12-month high, without the narrow-zone filter.
- No hindsight: percentile and zone boundaries use only data available before the breakout.

## Invalidation

The claim is rejected if the narrow-zone breakout does not improve forward-return distribution or drawdown after the fixed rule is tested out of sample.

## Required failure case

False breakouts during range-bound or regime-transition periods.

## Status

- Rule pre-registered: YES
- Historical test: RUNNING
- Out-of-sample result: PENDING
- Chapter status: NEEDS_REVISION
