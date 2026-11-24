# A Long Lower Wick Is Not a Forecast

Intermediate standalone lesson — internal draft, not assigned a public lesson number.

A candle can tell you how far price traveled below its body. It cannot tell you why every buyer or seller acted, or guarantee what comes next. A long lower wick is an observation about the range, not a forecast.

Consider two hypothetical sessions with identical open $100, high $102, low $94 and close $101. The body is $1, lower wick $6, upper wick $1, and total range $8. The lower wick occupies 75% of the range. In one market the previous three closes are $112, $108 and $104. In another they are $90, $94 and $98. The first candle appears after falling closes; the second appears after rising closes. The shape is identical, but the context is not. Neither establishes the probability of tomorrow's return.

Instead of naming the shape and immediately placing a trade, separate three questions: What did price do? Where did it happen relative to a predefined context? What evidence would make the interpretation wrong? For example, a close below $94 on a subsequent session would contradict a hypothesis that $94 will hold as support. It would not prove that the original wick had no buyers.

A quantitative test must define the shape before examining outcomes. One illustrative rule is lower wick at least twice the body, upper wick no larger than the body, positive range, and body at least 10% of range. These thresholds are teaching choices, not validated optimal settings. Compare subsequent returns against a baseline with comparable prior trend and volatility. Use only information available at the signal close; a next-open execution assumption avoids pretending the final candle was known earlier. Include costs and report sample size and uncertainty. Do not select thresholds on the test sample.

Exercise: O=100 H=102 L=94 C=101 meets all four illustrative rules: 6>=2, 1<=1, 8>0, 1/8=12.5%. O=100 H=102 L=94 C=100 does not meet the minimum body rule. This avoids division by zero and distinguishes the rule from a doji-like shape. Both examples are synthetic; no empirical performance claim is made.

## Internal evidence and status
Original mathematical derivation from stated hypothetical OHLC. Reference discovery: integration/research-catalog.json, topics hammer and doji; integration/offline-research-briefing.md, entry 3, 五种常见的看涨信号形态.pdf, source SHA 96356a177d3d6c1e1cac86ca7a7c184684f00482, candidate locators pages 10, 15, 16, 17. These are metadata only, not inspected original pages or evidence of agreement. No textbook chart was accessible in this session. Draft is complete as a standalone conceptual teaching unit, not textbook fusion or validated trading strategy. Next: inspect original source pages via authorized access and run an out-of-sample comparison on consistent OHLC data. No publication authorization.
