# Candlestick validation register — Evidence first
Authority: CONTINUITY-RULES.md, blob 5ae0fe1d8136ede9d81011f9df521f1ae4dbc391.
Purpose: seek truth, not confirmation of a preferred conclusion. Record all valid tests, favorable, unfavorable and inconclusive. No claim of predictive advantage without independent evidence and appropriate controls.

| ID | Research question | Status |
|---|---|---|
| C01 | Long-term reversal: hammer and shooting star | Mixed — [U.S. weekly/monthly matched study](us-candle-horizons/README.md); replication pending |
| C02 | Trend continuation | Pending |
| C03 | Trend exhaustion | Pending |
| C04 | Support and resistance | Pending |
| C05 | Breakout and false breakout | Pending |
| C06 | Wick/body price rejection and pressure proxies | Pending |
| C07 | Psychological interpretations | Pending |
| C08 | Incremental volume value | Pending |
| C09 | Daily/weekly/monthly confluence | Pending |
| C10 | Incremental MACD/RSI value | Pending |
| C11 | Risk invalidation levels | Pending |
| C12 | Cross-market robustness | Pending |

## Existing evidence (not long-term validation)
- SPY exploratory five-session study: [record](2026-11-25-spy-candle-backtest.md), 6454 rows, 73 hammers (43 direction matches), 53 stars (34 matches). Single third-party dataset, no matched controls or costs; not proof of advantage.
- Separate 200-event exploratory test reported in chat: 111 hammers (68 matches), 89 stars (47 matches), relaxed definitions; not independently reproduced in this register and not comparable with the prior test. No long-term conclusion.
- [Chart comparison notes](2026-11-25-hammer-shooting-star-market-comparison.md): original chart OHLC and independent vendor checks remain pending.

## Acceptance criteria
Freeze definitions before evaluation; use 20/60/120-session prior trend and 20/60/120/250-session outcomes. Seek at least 20,000 distinct eligible historical signals across instruments, markets and regimes; expand markets instead of weakening definitions. Report per-pattern counts, overlapping windows, cross-asset dependence, survivorship bias and out-of-sample results. Do not count raw bars, repeated runs or duplicate events as signals. Earlier 200-event results remain exploratory. Sample size alone does not establish validity. Record dataset provenance, adjustment policy, sample, benchmark, matched controls, uncertainty, overlap, positive and negative examples, reproducible code, chart data and limitations. Separate descriptive, predictive and economic advantages. Classify each as supported, mixed, unsupported or pending. No unsupported corrections to original materials.

## Comparative literature: horizon and exit-rule boundaries (2026-11-25)
- Marshall, Young & Rose (2006), JBF 30, 2303–2323, abstract and methodology, https://doi.org/10.1016/j.jbankfin.2005.08.001 : DJIA constituents 1992–2002, core ten-day tests; negative profitability evidence, not a fixed 250-session structural reversal test.
- Lu et al. (2012), abstract and introduction, https://doi.org/10.1016/j.rfe.2012.02.001 : Taiwan, opposite-pattern exits, some bullish reversal strategies positive; variable holding period differs from fixed horizons.
- Lu, Chen & Hsu (2015), abstract, https://doi.org/10.1016/j.jbankfin.2015.09.009 : results differ by exit strategy on DJIA data; cannot generalize to single-candle long-term reversal.
- Tharavanij et al. (2017), abstract, https://repository.li.mahidol.ac.th/handle/123456789/41618 : SET50, 1/3/5/10-day tests, generally weak results and no general improvement from indicator filters.

Original teaching card (intermediate): **A reversal signal is not a completed reversal.** A candle describes trading within one interval. A long-term reversal requires a subsequent change in market structure. Compare a predefined trend-matched control group at the same forward horizons; evaluate structural change separately from returns and profitability. Exercise (illustrative): if price rises from 100 to 105 after a hammer but later falls to 90, an early rally and a sustained reversal are different outcomes. At the two observation points returns are +5% and -10%; neither alone establishes a structural reversal. Answer: inspect dated swing structure and the full intervening path. No real-market sample added by this card; independent chart/OHLCV replication remains pending. Literature findings are external evidence, not textbook-page review.

## C08 — Volume and reversal: distinguish turnover from relative volume
External evidence: Lee & Swaminathan (2000), Journal of Finance 55, 2017–2069, https://doi.org/10.1111/0022-1082.00280, abstract and p. 2018 footnote 1. Historical share turnover is associated with momentum persistence and reversal timing in portfolios. This is not a test of a single-session hammer or 20-session relative volume. Status: pending direct replication; no textbook error established.

Original teaching card: **Volume Is Context, Not Confirmation by Itself.** Relative volume compares a session's shares traded with a prior-session baseline; turnover divides shares traded by shares outstanding. For an illustrative stock with 3.6 million shares traded, prior 20-session mean of 2 million and 100 million shares outstanding, relative volume is 1.8 and turnover is 3.6%. Exercise: if shares outstanding double while traded shares and baseline stay unchanged, relative volume remains 1.8 but turnover falls to 1.8%. Neither metric proves a trend reversal. Proposed test: compare fixed hammer definitions with and without a prespecified relative-volume filter against trend-matched non-hammer controls, using completed monthly/weekly bars and 20/60/120/250-session outcomes. Report negative cases, uncertainty and overlapping observations. Illustrative arithmetic checked; actual OHLCV comparison and textbook page review pending. No new market signals counted.

## Incremental information versus baseline (2026-11-26)
Lo, Mamaysky & Wang (2000), Journal of Finance 55(4), 1705–1765, https://doi.org/10.1111/0022-1082.00265, abstract and p. 1729 sections C–D; https://www.nber.org/papers/w7613. The authors compare conditional and unconditional return distributions and separately condition on changes in turnover. Their ten chart patterns and one-day return methodology do not directly validate hammer-based long-term reversals. For our study use prespecified trend-matched controls, fixed 20/60/120/250-session horizons, and compare incremental effects separately. Original teaching card: **Does a Chart Pattern Add Information?** Suppose a hammer group has a 60% reversal rate and its matched control has 58%. The observed difference is 2 percentage points, not 60 percentage points. Exercise: does this establish a reliable advantage? No; uncertainty, dependence and out-of-sample validation remain necessary. Hypothetical rates only; no real-market signal added. Previously delivered in chat; persisted here after duplicate check. Textbook page and OHLCV replication pending.

## Corporate-action normalization (2026-11-26)
Independent source: SEC Investor.gov glossary, Stock Split, https://www.investor.gov/introduction-investing/investing-basics/glossary/stock-split (definition and two-for-one example). Original teaching card: **A Stock Split Is Not a Market Crash.** Suppose 30 shares trade at $180 before a three-for-one split. Immediately after the mechanical adjustment, 90 shares at $60 still represent $5,400, assuming no market movement. Exercise: compare a subsequent close of $63 with the pre-split $180 close. Unadjusted comparison gives -65%; split-normalized price return is +5%. Normalize all OHLC fields consistently before constructing weekly and monthly candles; document volume adjustment separately and distinguish price returns from dividend-inclusive returns. This is an illustrative calculation, not a historical event or evidence of pattern performance. Actual market comparison and textbook locator pending. Previously discussed in chat; new independently sourced variant.
