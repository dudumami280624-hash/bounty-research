# Original research unit: A candle is not a return

Internal editorial draft — The Market Mind. Independent conceptual development; illustrative synthetic data, not a claim of textbook inspection or market backtesting.

## Beginner: Read two reference points
A candle describes a session relative to its open. A daily return compares its close with the preceding close. These comparisons answer different questions. Suppose yesterday closed at $100. Today opens at $94, trades between $92 and $98, and closes at $97. The candle is positive by $3, or 3.19% of the open, while the close-to-close return is negative 3%. A recovery within a session need not erase an overnight loss.

## Intermediate: Separate gap, body and range
For previous close P and open O, close C, high H and low L, define gap O/P−1, intraday return C/O−1, body |C−O|, upper wick H−max(O,C), lower wick min(O,C)−L. Require positive denominators and L≤min(O,C)≤max(O,C)≤H. The example has gap −6%, body $3, upper wick $1, lower wick $2 and range $6. The exact compounded return is (94/100)(97/94)−1=−3%; adding percentage returns is only an approximation.

## Advanced: Avoid information leakage
A completed candle cannot reveal the order in which its high and low occurred. Two intraday paths 94→92→98→97 and 94→98→92→97 have identical OHLC. A strategy whose stop and target both lie within that range cannot determine which was hit first using daily OHLC alone. Use finer time resolution or explicitly report ambiguous execution assumptions. Adjusted and unadjusted price series must not be mixed without accounting for corporate actions.

## Original teaching exercise
Previous close 50, open 52, high 53, low 49, close 51. Is the candle negative? Is the daily return positive? Answer: yes; body −1, close-to-close +2%, intraday −1.9231%, upper wick 1, lower wick 2. This exercise is synthetic and not a trade recommendation.

## Evidence status and next step
Arithmetic independently derived from the stated inputs. No reference textbook pages or actual market chart were inspected for this unit. Next: select an accessible historical OHLC series, document provider and adjustment conventions, and reproduce the same calculations with actual observations before attaching a real-market example. Keep this internal note separate from public-facing prose. No publication authorization.
