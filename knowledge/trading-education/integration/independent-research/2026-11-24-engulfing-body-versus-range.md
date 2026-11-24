# Independent research — Engulfing the body is not engulfing the range

2026-11-24 | Original unpublished teaching unit | Synthetic prices only

## Beginner: two different questions

A stock has been declining. Yesterday it opened at 100 and closed at 97, with a high of 105 and a low of 94. Today it opens at 96 and closes at 101, with a high of 102 and a low of 95. Today's body spans 96–101, covering yesterday's 97–100 body. Yet today's entire range sits inside yesterday's range. Both observations can be true. A bullish engulfing body is not necessarily an outside bar, and neither observation establishes a future return.

Reverse the directions after an advance: yesterday opens at 97 and closes at 100; today opens at 101 and closes at 96. The second body covers the first in the opposite direction. This is bearish engulfing geometry. Without the preceding advance, describe the geometry rather than automatically naming a reversal setup.

## Intermediate: an explicit classifier

Validate low <= min(open,close) <= max(open,close) <= high for each bar. Require opposite nonzero bodies. For bullish geometry require O2 <= C1 and C2 >= O1, with at least one strict inequality. For bearish geometry require O2 >= C1 and C2 <= O1, with at least one strict inequality. Separately flag outside range when H2 >= H1 and L2 <= L1, with at least one strict inequality. These are our inclusive-edge teaching conventions; a strict version requires both inequalities to be strict. TradingView allows equality at the body edges; ICICI Direct describes a stricter bullish example. Report sensitivity rather than silently mixing conventions.

| First OHLC | Second OHLC | Body geometry | Outside range |
|---|---|---|---|
| 100, 105, 94, 97 | 96, 102, 95, 101 | bull | no |
| 97, 102, 95, 100 | 101, 104, 94, 96 | bear | yes |
| 100, 105, 94, 97 | 98, 106, 93, 101 | none | yes |
| 100, 105, 94, 97 | 97, 102, 96, 101 | bull | no |
| 100, 105, 94, 97 | 97, 102, 96, 100 | none | no |
| 100, 105, 94, 97 | 96, 99, 95, 101 | invalid | N/A |

Six synthetic cases passed executable JavaScript checks of the rules above on 2026-11-24. This tests classification, not predictive performance.

## Advanced: design a falsifiable study

Freeze the prior trend definition before looking at returns: for example, use the sign of the return from close t-6 to close t-2, where t is the second pattern bar. Exclude zero returns or label them neutral. Compare engulfing candidates with opposite-color pairs without engulfment under the same trend and volatility buckets. Record both inclusive and strict edge variants, and outside-range status separately. Use consistently split-adjusted OHLC, avoid mixing adjusted close with raw open, and include delisted securities if studying a historical universe. Observe the signal only after t closes; a hypothetical executable entry is next session's open, not the already observed close. Measure forward returns to the close of session t+5, deduct explicit trading costs, and report sample sizes, median, dispersion and uncertainty. For overlapping windows use nonoverlapping samples or dependence-aware inference. Hold out later dates; do not optimize thresholds on the test set.

A failed bullish example: after the first table pair, suppose the next session opens at 99 and closes at 93. The engulfing geometry remains true even though price falls below both prior lows. Do not remove such examples from a study. A break above the pattern high is a separate confirmation rule, not part of the body definition. A gap through an invalidation level may produce a worse fill than the level itself.

## Practice and answers

1. Does row one engulf the first candle's high and low? No; only the body is engulfed.
2. Why is row three not a bullish engulfing? Its second open is above the first close, leaving part of the first body uncovered.
3. Why does row four qualify under the inclusive rule but not the strict rule? The lower body boundaries coincide.
4. Why reject row six? The second close exceeds its reported high.
5. Can a green second candle guarantee a reversal? No; neither color nor body coverage supplies a validated forecast.

## Sources and scope

- Fidelity, Identifying Chart Patterns with Technical Analysis, engulfing section: https://www.fidelity.com/bin-public/060_www_fidelity_com/documents/learning-center/Idenitfying-Chart-Patterns.pdf — body-based definition and caution about breakout direction.
- TradingView, Bullish Engulfing: https://www.tradingview.com/support/solutions/43000583771-bullish-engulfing-recognizing-buyers-taking-over-at-a-downtrend-s-base/ — inclusive boundary description, wick distinction.
- ICICI Direct, Understanding Bullish Engulfing Pattern: https://www.icicidirect.com/ilearn/technical-analysis/articles/understanding-bullish-engulfing-pattern — stricter opening and closing description.
- Fidelity-hosted Thomas Bulkowski, Investment Candles: https://www.fidelity.com/bin-public/060_www_fidelity_com/documents/InvestmentCandles2.pdf — context changes conventional pattern interpretation; no reported performance statistics adopted here.

Public source descriptions checked 2026-11-24. Original examples and study design; no textbook excerpts, real-market backtest, original-source semantic verification or publication claim. Educational material, not a recommendation.
