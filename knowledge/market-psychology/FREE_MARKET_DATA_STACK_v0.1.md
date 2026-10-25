# Free Market Data Stack v0.1

## Approved free sources

1. Nasdaq Historical Data / Nasdaq Data Link
   - Daily OHLCV and market activity.
   - Historical access depends on the public or registered endpoint.

2. SEC MIDAS Market Structure Data Downloads
   - Spreads and depth.
   - Trade-order volume.
   - Cancel-trade ratio.
   - Hidden and odd-lot activity.
   - Quote-life distributions.

3. FRED, Federal Reserve and BLS
   - Rates, CPI, employment, policy and macro controls.

## Research boundary

This stack supports market activity, aggregate market-structure indicators and causal controls. It does not provide complete event-specific TAQ for every historical date. A chapter must state the exact coverage period and must not label aggregate MIDAS metrics as full order-level data.

## Frozen decision

Do not purchase Polygon, Tiingo, Databento or TAQ for the first version. Use the free stack for the first reproducible experiments and mark unavailable fields explicitly.
