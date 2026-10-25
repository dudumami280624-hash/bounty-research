# Chapter 01 Empirical Test Specification v0.1

## Claim

A change in market interpretation can transmit through attention, positioning and order flow, but narrative must add information beyond price history alone.

## Pre-registered proxy

Primary proxy: dated public information event with an observable policy, earnings or crisis announcement.
Market response: next-session and 5-session excess return, volume change and realized volatility.
Control benchmark: matched non-event sessions and a price-only momentum baseline.

## Data required

- event date and event classification
- SP500 or Shiller Composite return
- volume and volatility where available
- FEDFUNDS, CPI, unemployment or earnings surprise when relevant
- publication timestamp and information availability

## Test

1. Freeze event list before inspecting outcomes.
2. Compare event-window returns with matched non-event windows.
3. Estimate mean and median excess return.
4. Bootstrap confidence interval.
5. Repeat in-sample and out-of-sample.
6. Report null and negative results.

## Causal identification

Treatment: the dated information event.
Outcome: post-event excess return, volume and volatility.
Counterfactual: matched sessions without the event.
Main confounders: simultaneous macro releases, market trend, liquidity and positioning.
Causal claim is blocked unless event timing and competing explanations are documented.

## Current status

- Hypothesis registered: YES
- Market data available: YES
- Event-level narrative dataset: NOT YET INGESTED
- Microstructure data: NOT YET INGESTED
- Statistical result: NOT RUN
- Chapter status: NEEDS REVISION
