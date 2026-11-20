# The Market Mind — Lesson 03
## Revised editorial draft
**Title:** What Can One Candlestick Really Tell You?  
**Deck:** A green candle can hide a losing day. A red candle can hide a gain.  
**Status:** DRAFT — editorial revision only; not approved for publication.

---

# What Can One Candlestick Really Tell You?

**The chart is green. Your investment is down. And both numbers can be correct.**

Imagine checking a stock chart after the closing bell.

You see a green candlestick. The stock closed above its opening price.

Then you check the previous close. The stock is down.

Nothing is wrong with the arithmetic. You are looking at two different measurements.

That distinction is easy to miss—and it can change the story you think a chart is telling.

In Lesson 02, we examined how a stock split can make a historical price comparison misleading when the basis is wrong. This lesson applies the same discipline to a single candlestick.

**A candle records prices. It does not record intentions.**

## 1. A green candle on a losing day

Consider Northstar, a fictional company.

| Price reference | Value |
|---|---:|
| Previous close | $110 |
| Today's open | $100 |
| Today's high | $107 |
| Today's low | $98 |
| Today's close | $105 |

Under the common convention in which a candle is green when its close is above its open, Northstar prints a green candle.

The open-to-close change is:

\[
(105-100)/100=+5.00\%
\]

But compared with the previous close:

\[
(105-110)/110\approx-4.55\%
\]

Both calculations are correct. They answer different questions.

Northstar opened $10 below the previous close, a gap down of approximately 9.09%. It then **closed 5% above its opening price**, recovering part—but not all—of that gap.

It did not close above the previous session's close.

**A green candle is not the same thing as a positive close-to-close return.**

*Figure 1 — Two valid comparisons of the same fictional session. Clearly label the previous close, open, high, low and close. Show +5.00% open-to-close and −4.55% close-to-close. Do not imply an unobserved intraday path.*

## 2. A red candle on a winning day

Now reverse the example.

| Price reference | Value |
|---|---:|
| Previous close | $100 |
| Today's open | $106 |
| Today's high | $108 |
| Today's low | $102 |
| Today's close | $103 |

Under the same open-versus-close convention, this is a red candle: the close is below the open.

Open-to-close:

\[
(103-106)/106\approx-2.83\%
\]

Close-to-close:

\[
(103-100)/100=+3.00\%
\]

The candle is red, yet the stock finished 3% above the previous close.

The opening gap explains the difference.

Some charting platforms allow different candle-color rules. Always check the chart's legend or settings before interpreting color.

**Color is a display convention. The prices are the evidence.**

## 3. What the body and shadows measure

A candlestick summarizes four prices for a chosen period: open, high, low and close.

For Northstar's first example:

- Body: $105 − $100 = $5.
- Upper shadow: $107 − $105 = $2.
- Lower shadow: $100 − $98 = $2.
- High-to-low range: $107 − $98 = $9.

The close was $7 above the low within a $9 range, or approximately 77.8% of the way from the low to the high.

These are measurable properties of the recorded prices.

But OHLC data alone do not reveal the exact order in which the high and low occurred, the path between them, or the identity and motives of the traders involved.

A daily candle compresses a trading period into four values. That compression is useful—but it leaves information out.

*Figure 2 — Candlestick anatomy. Label O=$100, H=$107, L=$98, C=$105; body=$5, upper shadow=$2, lower shadow=$2, total range=$9. Include a note that the example is fictional.*

## 4. The same candle in a different context

Imagine the same OHLC candle appearing after three different price histories:

- After a sustained advance.
- After a prolonged decline.
- Inside a sideways trading range.

The candle's four prices have not changed. The surrounding evidence has.

After an advance, an analyst may examine whether the broader move is continuing or changing. After a decline, the analyst may investigate whether the session is part of a recovery or only a temporary rebound. Inside a range, the candle's position relative to the range boundaries may matter more.

These are questions to investigate, not conclusions guaranteed by the candle.

**A candlestick is a measurement. A market interpretation is a hypothesis.**

*Figure 3 — Three hypothetical price sequences ending in the same OHLC candle. Use consistent, fictional data and label each context. Do not attach predictive success rates.*

## 5. What volume adds—and what it cannot establish

Suppose Northstar's reported volume is three million shares, compared with a recent average of one million shares over a clearly specified period.

That tells us trading activity was higher than the chosen reference.

It does not, by itself, explain why.

A company announcement, broader market news, portfolio rebalancing or several overlapping events could contribute. The volume figure alone cannot distinguish among those explanations.

Every executed share trade has both a buyer and a seller. High volume does not mean shares were bought without being sold.

Volume can add useful context, but interpretation depends on the instrument, venue, session, aggregation method and data source. State those details when they matter.

Do not turn high volume plus a green candle into proof of institutional accumulation. That claim requires evidence beyond a single OHLCV bar.

## 6. Separate observation from inference

Consider three claims:

**Observation:** “The stock closed $5 above its opening price.”  
This follows directly from the example's recorded prices.

**Description:** “The close was about 77.8% of the way from the session low to the session high.”  
This is a calculation from the same data.

**Inference:** “Institutions are accumulating shares and a rally will begin tomorrow.”  
The candle does not identify the participants, establish their motives or predict tomorrow's price.

Use the Five-Line Chart Receipt from Lesson 02:

1. Security.
2. Timeframe.
3. Data basis and session.
4. Verified observation.
5. Unproven interpretation.

Then ask what happened before the candle and what the volume data actually measures.

The goal is not to ban interpretation. It is to label it honestly and test it against alternative explanations.

## 7. Test your reading

A fictional stock has these prices:

| Measurement | Price |
|---|---:|
| Previous close | $80 |
| Open | $84 |
| High | $86 |
| Low | $81 |
| Close | $82 |

Before reading the answers, ask:

1. Is the candle green or red under the conventional open-versus-close rule?
2. Is the close above or below the previous close?
3. How large is the upper shadow?
4. Where did the close fall within the day's high-low range?
5. What can this candle establish about tomorrow?

**Answers**

1. Red: $82 is below the $84 open.
2. Above the previous close by 2.50%: ($82−$80)/$80.
3. $2: the high of $86 minus the open of $84.
4. 20% of the way from the low to the high: ($82−$81)/($86−$81).
5. Nothing conclusive about tomorrow's direction.

One more question matters even more:

Two analysts see the same candle. One says buyers are taking control. The other says the stock is simply trading within a larger range. What additional evidence would help distinguish those explanations?

That is the habit this lesson is designed to build.

## The question to ask before believing a chart

When you see a striking candle, ask:

**What happened?** Record the prices, timeframe and source.

**What am I assuming?** Separate the data from the story you are adding.

**What evidence could challenge my explanation?** Consider alternative causes and missing information.

A chart can make an explanation look obvious. That does not make it proven.

**A candle records prices. It does not record intentions.**

## Your Market Mind challenge

Find a historical candlestick. Record its open, high, low, close and previous close. Calculate both the open-to-close and close-to-close changes.

Then write one statement the data directly supports—and one claim the candle alone cannot establish.

**Have you ever seen a green candle on a down day, or a red candle on an up day? What comparison changed your interpretation?**

Share the example and the evidence you used.

## Next lesson

### Why One Candlestick Is Never the Whole Story

One candle gives us a limited view of a trading period. Markets, however, form sequences of prices—highs, lows, ranges and changing structures.

In Lesson 04, we'll examine how multiple candles create price structure, and why a convincing pattern still needs evidence before it becomes a useful conclusion.

**THE MARKET MIND**  
*Evidence first. Think independently.*  
*Educational content only. Not financial advice.*

---

## Research references — pending source-level verification

- StockCharts ChartSchool, “Introduction to Candlesticks”: https://chartschool.stockcharts.com/table-of-contents/chart-analysis/candlestick-charts/introduction-to-candlesticks
- StockCharts ChartSchool, “What Are Charts?”: https://chartschool.stockcharts.com/table-of-contents/chart-analysis/what-are-charts
- StockCharts ChartSchool, “Candlesticks and Traditional Chart Analysis”: https://chartschool.stockcharts.com/table-of-contents/chart-analysis/candlestick-charts/candlesticks-and-traditional-chart-analysis
- StockCharts ChartSchool, “CandleVolume”: https://chartschool.stockcharts.com/table-of-contents/chart-analysis/chart-types/candlevolume

**Data note:** Northstar and all prices in this lesson are fictional teaching examples, not historical market data, tested trading signals or investment recommendations.

## Editorial QA — current status

- [x] Reworked opening around the reader's real comparison error.
- [x] Added the opposite red-candle/positive-day example.
- [x] Replaced wording that could imply an unobserved intraday path.
- [x] Reduced repeated claims about prediction and institutional intent.
- [x] Added a question testing evidence-based reasoning.
- [x] Recalculated the fictional examples and candle geometry.
- [ ] Verify every external source against the exact claims and record access date/section.
- [ ] Cross-check relevant passages and figures in the 178-source course archive; not yet completed.
- [ ] Produce and inspect cover and three data-led figures; figures must be built from verified numbers, not AI-rendered text.
- [ ] Add final captions and ALT text after figures are created.
- [ ] Verify the X Article's final layout and mobile/desktop rendering.
- [ ] User approval required before publication.

**Status remains DRAFT. This revision does not certify the 178-source audit as complete.**
