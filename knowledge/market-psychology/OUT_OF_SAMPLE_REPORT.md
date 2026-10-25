# Out-of-Sample Report v0.1

Status: RUN — BASELINE TREND TEST COMPLETE

Evaluation split is fixed in BACKTEST_CONFIG.yaml:

- In-sample: 1929–1999
- Validation: 2000–2009
- Out-of-sample: 2010–2025

## Fixed experiment

- Dataset: Robert Shiller S&P Composite monthly series
- Rule: 10-month moving average versus 50-month moving average
- Signal timing: prior observations only
- Cost: 12 bps per position change
- Benchmark: buy and hold

## Out-of-sample result: 2010–2025

| Metric | Buy and hold | Trend 10/50 |
|---|---:|---:|
| Cumulative return | 507.08% | 311.06% |
| Annualized return | 12.00% | 9.29% |
| Volatility | 11.45% | 11.03% |
| Maximum drawdown | -20.29% | -21.27% |

## Conclusion

The fixed 10/50 rule did not outperform buy and hold out of sample. It also did not reduce maximum drawdown in this period. The baseline hypothesis that a simple trend rule improves broad-market outcomes is rejected for this parameterization and sample.

## Still pending

- Bootstrap confidence interval in the final report
- Parameter sensitivity without changing the pre-registered primary rule
- Microstructure-aware transaction-cost sensitivity
- Out-of-sample tests for the other registered hypotheses

No chapter is marked VERIFIED from this result alone.
