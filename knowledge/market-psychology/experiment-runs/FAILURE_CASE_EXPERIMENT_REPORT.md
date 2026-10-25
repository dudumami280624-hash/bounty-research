# Failure Case Experiment Report v0.1

Rule: 10/50 monthly moving-average trend rule, prior observations only, 12 bps cost per position change. Benchmark: buy and hold. Data: Shiller S&P Composite monthly series.

| Case | Buy/hold cumulative | Trend cumulative | Buy/hold max DD | Trend max DD |
|---|---:|---:|---:|---:|
| 2000–2002 | -36.31% | -28.73% | -42.47% | -30.80% |
| 2007–2009 | -23.18% | -33.42% | -50.82% | -38.01% |
| 2010–2011 | 10.45% | -8.67% | -12.29% | -12.72% |
| 2020 | 11.72% | 10.26% | -19.09% | -19.31% |
| 2022 | -16.20% | -17.32% | -20.29% | -21.27% |

## Result

The same fixed rule behaves differently across failure cases. It reduced drawdown in 2000–2002 and 2007–2009 but lost more than buy-and-hold in 2007–2009, 2010–2011, 2020 and 2022 on cumulative return. This is evidence of regime dependence, not universal superiority.

Full machine-readable results: failure_cases_results.json.
