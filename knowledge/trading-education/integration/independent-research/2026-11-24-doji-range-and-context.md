# Independent research unit — A doji is not a forecast

2026-11-24 | Beginner / intermediate bridge | Original instructional prose, unpublished.

## Teaching text

Two candles can have identical opening and closing prices yet tell very different stories about the trading range. Imagine a stock opening at $100, reaching $106 and $94, and closing at $100. Now imagine another session opening and closing at $100 but trading only between $99.80 and $100.20. Both satisfy an exact open-equals-close definition of a doji. The first spans twelve dollars; the second spans forty cents. Neither tells us which extreme came first.

Start with measurement rather than a pattern name. For an ordinary OHLC candle, subtract the low from the high to measure its range. Subtract the smaller of the opening and closing prices from the larger to measure its body. A small body relative to the range means the two endpoints are close compared with the excursion between extremes. It does not establish the number of buyers or sellers, their intentions, or the direction of tomorrow's price.

A near-doji needs an explicit rule. For this classroom exercise only, use body/range <= 0.05 when range is positive. This is our illustrative threshold, not an industry standard or a tested trading edge. A zero-range candle has no defined ratio; keep it in a separate category. Use the same session definition and price adjustment convention across comparisons.

Context changes the question. After a sustained rise, a small-body candle might prompt us to investigate whether momentum is fading. Inside a sideways market it may be unremarkable. After a decline it may invite a different hypothesis. None of these contexts establishes a reversal. A later close outside the candle's range is a new observation, not proof of what will happen next.

## Worked examples (synthetic, not historical market data)

| Open | High | Low | Close | Body | Range | Body/range | Upper wick | Lower wick |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 100 | 106 | 94 | 100 | 0.00 | 12.00 | 0.00% | 6.00 | 6.00 |
| 100 | 100.2 | 99.8 | 100 | 0.00 | 0.40 | 0.00% | 0.20 | 0.20 |
| 100 | 106 | 94 | 100.3 | 0.30 | 12.00 | 2.50% | 5.70 | 6.00 |
| 100 | 106 | 94 | 105 | 5.00 | 12.00 | 41.67% | 1.00 | 6.00 |

The third example meets our near-doji rule; the fourth does not. The first two have identical body ratios but a 30-fold difference in range. Compare range with recent ranges before assigning significance.

## Exercise and answer

Suppose the first example is followed by a close at $107. What can you establish? The next close exceeded the earlier high by $1. What remains unknown? Whether the move persists, whether an executable entry existed at the assumed price, and whether any strategy has positive expectancy after costs. If instead the next close is $93, the same original doji preceded a downside break. Both scenarios are possible; neither is a probability estimate.

## Intermediate extension

To test a hypothesis, define the universe, session, near-doji threshold, trend context, entry timing, holding period and transaction costs before evaluating outcomes. Compare against a baseline with the same market and trend context. Avoid using future bars to label a signal available at today's close. Report sample size and out-of-sample results. No backtest was conducted here.

## Internal evidence notes

- Schwab thinkorswim Candle Chart: https://schwab.tos.mx/center/howToTos/thinkManual/charts/Chart-Modes/Chart-Types/candle — accessed 2026-11-24; supports OHLC geometry and exact equal-open-close platform definition.
- Fidelity, What is technical analysis?, June 10 2026: https://www.fidelity.com/learning-center/trading-investing/technical-analysis/what-is-technical-analysis — accessed 2026-11-24; supports trend context and limitations of technical signals.
- The repository's doji reference materials remain candidates for source-level comparison; no original pages inspected in this unit. This is independent supplemental research, not completion of any of the 178 source documents.
- Numerical check executed in JavaScript: all four examples satisfy body + upper wick + lower wick = range within 1e-9; ratios computed from supplied OHLC. No empirical performance claim.
