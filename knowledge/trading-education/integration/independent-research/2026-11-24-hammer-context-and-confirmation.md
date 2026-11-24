# Independent research unit — Same wick, different context

2026-11-24 | Beginner to advanced bridge | Original unpublished teaching text

## Beginner: read the candle before naming it

Imagine a stock that has fallen from 105 to 99 to 95. Its next session opens at 91, touches 82, reaches 93 and closes at 92. The close is near the high, despite the much lower price recorded during the session. That is hammer-like geometry. In a declining market, technicians call it a hammer. Put the very same candle after a sustained advance and the conventional name becomes hanging man. The shape is unchanged; the preceding price history changes the interpretation.

Now reverse the wick: open 91, high 101, low 90, close 92. The market reached a much higher price but finished near the bottom of its range. After a decline this is inverted-hammer geometry; after an advance it is shooting-star geometry. Neither color alone decides the name. OHLC does not reveal the exact sequence of intraday highs and lows, the identities of participants, or their motives.

## Intermediate: measure rather than guess

For valid OHLC data, body B=abs(C-O), upper wick U=H-max(O,C), lower wick D=min(O,C)-L, range R=H-L. Reject inconsistent prices. Our illustrative classifier requires R>0 and B>0. A lower-wick candidate has D>=2B, U<=0.1R and the entire body in the top third. An upper-wick candidate reverses those conditions. These are explicit teaching thresholds, not universal definitions or optimized parameters. Zero-body bars belong in a separate doji analysis.

| O | H | L | C | B | U | D | R | Geometry |
|---:|---:|---:|---:|---:|---:|---:|---:|---|
| 91 | 93 | 82 | 92 | 1 | 1 | 9 | 11 | lower wick |
| 91 | 101 | 90 | 92 | 1 | 9 | 1 | 11 | upper wick |
| 92 | 93 | 82 | 91 | 1 | 1 | 9 | 11 | lower wick |
| 91 | 96 | 87 | 92 | 1 | 4 | 4 | 9 | neither |
| 91 | 91 | 91 | 91 | 0 | 0 | 0 | 0 | neither |

All examples are synthetic, not historical quotes. The third row demonstrates that a red body can meet our lower-wick rule. The fourth has substantial shadows on both sides. The fifth has no range and cannot be classified by wick ratios.

Suppose the first candle is followed by a session closing at 94. A strict follow-through rule (close above 93) is satisfied. A different next session closing at 81 would instead break the pattern low. These are alternative scenarios, not predictions. A close at 92.5 exceeds the body top but not the high: this illustrates why confirmation definitions must be written before evaluating outcomes. CMC describes body-based confirmation, while Capital.com describes high-based confirmation for a hammer. They are different rules, not interchangeable evidence of profitability.

## Advanced: turn the interpretation into a testable hypothesis

Define a prior decline using only completed bars, for example C[t-1] < C[t-2] < C[t-3]. Compare the raw candidate and strict follow-through groups against all comparable declining-market dates. Use next-session executable prices after the signal is known; for confirmation at t+1 close, use t+2 open or a separately justified execution model. Measure fixed-horizon returns, drawdowns and sample counts. Include transaction costs, gaps, splits, delisted stocks and liquidity filters. Separate development and holdout periods; account for overlapping events and multiple comparisons. Do not optimize wick thresholds on the holdout. No empirical edge is claimed here: a recognizable shape and a profitable rule are separate propositions.

## Exercise and answer

A candle opens at 92, reaches 93, falls to 82 and closes at 91 after three rising closes. Is it a bullish hammer? Answer: no under the conventional context naming; it has lower-wick geometry after an advance, so it is a hanging-man candidate. A subsequent close below 82 would satisfy one possible bearish follow-through rule, not guarantee further losses.

## Evidence and limits

- TradingView, [Hammer](https://www.tradingview.com/support/solutions/43000583775-bullish-hammer-detecting-a-possible-bottom-in-a-downtrend/) and [Inverted hammer](https://www.tradingview.com/support/solutions/43000583780-bullish-inverted-hammer-spotting-early-buying-signals-in-a-downtrend/): conventional geometry and prior decline.
- [CMC Markets, inverted hammer guide](https://www.cmcmarkets.com/en-gb/trading-strategy/inverted-hammer-candlestick-pattern): body-based follow-through and failure caveat.
- [Capital.com, hammer guide](https://capital.com/en-int/learn/technical-analysis/hammer-candlestick-pattern): high-based follow-through and context distinction.
- [Fidelity, Identifying Chart Patterns](https://www.fidelity.com/bin-public/060_www_fidelity_com/documents/learning-center/Idenitfying-Chart-Patterns.pdf), section Shooting Star and Inverted Hammer: conventional interpretation and caution about single-pattern performance.

Sources consulted 2026-11-24. These are educational definitions, not independent empirical proof. Numerical fixtures checked by executable arithmetic and classification assertions (5/5). No market backtest performed. No original textbook pages inspected; this unit does not increment the 178-source review count. Educational only, no investment recommendation or return promise.
