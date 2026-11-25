# U.S. weekly and monthly candlestick comparison

Run and data cutoff: November 25, 2026. Status: executed historical study with mixed results and no independent replication. C01 in the [validation register](../candlestick-validation-register.md).

## Scope and counts

- Final universe: 604 requests from the [current S&P 500 constituent file](https://github.com/datasets/s-and-p-500-companies/blob/main/data/constituents.csv), SPY, and a deterministic supplemental selection of 100 NYSE-listed common stocks outside the constituent file, selected before running the expansion. NKE and DAL were explicit instruments and deduplicated against the constituents. The [Nasdaq Trader directory](https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt) supplied the supplementary listing universe.
- 599 usable histories. Five excluded for insufficient history or failed symbol/currency/history validation: FDXF, HONA, VYLR, JMKE, and ADIG. 4,243,001 source day rows. Derived 878,758 completed weekly and 201,334 completed monthly bars after quality filters, including bars without a signal.
- 22,173 eligible ticker/timeframe events, 22,149 matched pairs, and **22,101 distinct ticker and trading-session dates** after cross-timeframe deduplication. This is a count of distinct events, not independent observations. Weekly and monthly overlaps and market-wide dependence remain.
- The intermediate S&P 500 stage had 501 usable histories and 19,199 eligible events. Its full subgroup results are retained in `summary.json`. The extension used the same analysis code and thresholds.

## Longest horizon in each timeframe

Success is a positive price change for a hammer and a negative price change for a shooting star, measured from the next bar's open to the terminal close. The weekly horizon is 52 bars. The monthly horizon is 12 bars. “pp” is the signal hit rate minus the matched control hit rate in percentage points.

| Timeframe | Signal date | Pattern | Eligible events | Signal hits | Matched control hits | Difference |
| --- | --- | --- | ---: | ---: | ---: | ---: |
| weekly | 2016 onward | shooting star | 3093 | 1029/3093 (33.27%) | 1130/3093 (36.53%) | -3.27 pp |
| weekly | Before 2016 | shooting star | 7795 | 2413/7795 (30.96%) | 2375/7795 (30.47%) | 0.49 pp |
| weekly | 2016 onward | hammer | 2432 | 1652/2431 (67.96%) | 1616/2431 (66.47%) | 1.48 pp |
| weekly | Before 2016 | hammer | 4544 | 2949/4544 (64.90%) | 2988/4544 (65.76%) | -0.86 pp |
| monthly | 2016 onward | shooting star | 889 | 298/889 (33.52%) | 353/889 (39.71%) | -6.19 pp |
| monthly | Before 2016 | shooting star | 1656 | 484/1655 (29.24%) | 514/1655 (31.06%) | -1.81 pp |
| monthly | 2016 onward | hammer | 581 | 375/564 (66.49%) | 367/564 (65.07%) | 1.42 pp |
| monthly | Before 2016 | hammer | 1183 | 743/1178 (63.07%) | 740/1178 (62.82%) | 0.26 pp |

## What the comparison shows

- In the 2016-onward group, both hammer timeframes were modestly better than their controls at the roughly one-year horizon. The weekly result was slightly negative before 2016. The monthly result before 2016 was close to its baseline.
- Shooting stars trailed their controls at the roughly one-year horizon in the 2016-onward group. The 2016-onward monthly shooting-star comparison was positive at three and six months, then negative at twelve months. This is why the same outcome horizon should be stated whenever reporting results.
- Illustrative monthly hammers: DAL, April 2020, +88.06%, and NKE, March 2022, -8.78%, from the next monthly open to the 12th monthly close. The private comparison figure is generated from vendor prices by `plot_examples.py`. These are two outcomes under the same test definition.

## Method and limits

Use Yahoo Finance USD daily quote OHLC available from January 1990 through the cutoff. Aggregate actual weekday rows into weeks ending Friday and calendar months. Exclude broken rows and the first and potentially incomplete final periods. Use the vendor quotation price series, not dividend-inclusive adjusted-close returns. See [Yahoo Finance's historical-price field labels](https://finance.yahoo.com/quote/NKE/history/). Corporate-action coverage and the individual chart prices were not reconciled with a second provider.

The preceding moves must agree in sign at 4/13/26 weekly bars or 1/3/6 monthly bars. A candidate must have a positive real body no larger than 35% of the range, a dominant wick at least twice the body, and the opposite wick no larger than 15% of the range. Hammer follows an eligible decline. Shooting star follows an eligible rise. Evaluate 13/26/52 weekly or 3/6/12 monthly bars and require the full longest horizon. Pair without replacement with a nonsignal on the same instrument, in the same trend direction and date cohort, within 730 calendar days, minimizing differences in those three prior log returns. This is retrospective matching, not a real-time trading rule. Controls can occur before or after the signal. Cohorts are descriptive pre/post-2016 slices, not a dedicated unseen holdout.

Current listing rosters introduce survival and membership bias. Price returns omit dividends, fees, slippage and short-borrow costs. Overlapping observations and cross-stock correlation have not been accounted for with dependence-aware confidence intervals. The close direction is a testable outcome and may differ from a structural reversal. Status for both patterns: mixed by timeframe, horizon, and cohort. Evidence is insufficient to establish a dependable trading advantage.

## Reproduction

Run `python3 fetch.py`, `python3 analyze.py data --cutoff 2026-11-25`, and `python3 audit_counts.py` from this directory. `manifest.json` preserves the exact test tickers and hashes of both listing inputs and each retrieved history. Vendor data and current listings can change; compare hashes when reproducing. `summary.json` preserves all horizon metrics, including equal-ticker weighting and median signed-return differences. `plot_examples.py` requires Matplotlib.
