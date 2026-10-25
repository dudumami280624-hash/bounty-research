# Baseline Experiment Report v0.1

Dataset: Robert Shiller S&P Composite monthly series.
Rule: 10-month moving average versus 50-month moving average; position is 1 when fast average exceeds slow average. One-way position-change cost: 12 bps. Signals use prior observations.

## Results

| Period | Buy and hold annualized | Trend annualized | Buy and hold max drawdown | Trend max drawdown |
|---|---:|---:|---:|---:|
| 1929–1999 | 5.95% | 4.22% | -84.76% | -58.44% |
| 2000–2009 | -2.71% | -5.07% | -50.82% | -42.03% |
| 2010–2025 | 12.00% | 9.29% | -20.29% | -21.27% |

## Interpretation

This fixed 10/50 rule reduced historical drawdown in the long in-sample period but did not outperform buy-and-hold in the validation or out-of-sample periods. It is therefore not evidence that the rule adds return value. The result is retained as a negative or mixed result and must not be used as a claim that trend following is superior.

## Limits

This is a baseline experiment, not a complete test of the Market Mind framework. It uses monthly index data, a simple cost assumption and no microstructure data. Further tests must be pre-registered before parameter changes.
