# Chapter 01 Microstructure Data Register v0.1

| Dataset | Variable | Source | Status |
|---|---|---|---|
| FRED SP500 daily | close, return | FRED SP500 | INGESTED |
| FOMC event dates | announcement date | Federal Reserve FOMC calendar | INGESTED for 2022 |
| Matched non-event sessions | close, return | FRED SP500 | PENDING |
| Daily volume | market activity proxy | exchange/index data source | PENDING |
| Bid-ask spread | execution cost/liquidity | TAQ or exchange data | PENDING |
| Order imbalance | order-flow transmission | TAQ/SEC event data | PENDING |
| Trading halts/circuit breakers | market mechanism | SEC historical reports | SOURCE LINKED |

## Rule

Price reaction alone cannot be labeled microstructure evidence. Until volume, spreads or order-flow data are attached, the chapter may claim only an event-return association.
