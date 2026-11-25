# Lesson 04 — last30days execution audit

Run date November 25, 2026. Requested evidence window October 26–November 25, 2026. The local engine completed and saved its raw output. The first-party X connection remains unavailable in this run.

## What was actually executed

- Upstream [last30days v4.6.0](https://github.com/mvanhorn/last30days-skill/releases/tag/v4.6.0), pinned to commit `64b1f006f800640022ce07f51de5ce56aad34b76`. Python 3.12.14. Optional YouTube dependency yt-dlp 2026.11.23 installed into the isolated workspace.
- Preflight and live doctor completed. Browser cookie reads disabled. No paid API keys or hosted backend used. Research invoked the local Python engine with `--no-browser-cookies --search reddit,youtube,hackernews --subreddits=TradingView,stocks,Daytrading --as-of 2026-11-25 --quick --emit=compact --plan -` and an external plan. The engine reported Reddit and YouTube active.
- A separate GitHub control completed in 5.6 seconds with two evidence records after filtering. The Lesson 04 run exited zero in 107.1 seconds and saved the Markdown output. Follow-up cache ID `b6ab33f7d1db47ec90ab130cfac6b8dd`.

## Source judgment

| Source | Observed result | Editorial decision |
| --- | --- | --- |
| Reddit | Public endpoints returned HTTP 403. The keyless fallback retrieved 30 candidates, dropped 28, and kept two. | Reject both retained items for this lesson. One was about a TradingView change and the other a holiday discussion. |
| YouTube | Six retrieved videos, zero within the requested dates, five retained by the engine. Comment probes timed out. The quick profile skipped transcripts. | Treat these five videos as historical background. Exclude their aggregate views from the 30-day trend assessment. |
| X | Engine doctor found no configured X connection. Public web search found an [older Turkish candlestick post](https://x.com/orhnrck/status/1887855089039147081). | No verified in-window X outlier. Keep the older post as a search lead only. |
| Supplemental public discovery | A [beginner YouTube clip](https://www.youtube.com/watch?v=yXFhBH5z3Hw) is dated October 31, 2026 in the search index. A direct command-line probe for this video timed out. | Within the window, useful for seeing the common OHLC angle. No independent engagement benchmark, so do not label it a breakout. |
| Independent market evidence | [MarketWatch's intraday report](https://www.marketwatch.com/livecoverage/nvidia-huang-reinstate-ceo/card/all-the-action-in-nvidia-s-stock-happened-within-the-first-90-minutes-lrAgy9jpWJqpfw77uCxV) puts both the $171.50 high and $156.93 low in the first hour of regular trading. | The report supplies a time window. Exact first-touch timestamps and ordering remain unverified. Daily prices remain recorded in the [NVDA case notes](../../../market-psychology/cases/nvda-2026-11-chart-notes.md). |

## Editorial outcome

The engine passes execution and output capture. Its raw report fails topic precision and recent-X coverage for this lesson. The published-content workflow adds a human relevance and date check before an item can justify an angle. For this run, lead with a question a learner can test on the existing chart: “Nvidia hit $171.50 and $156.93 on Nov. 23. Can you tell which came first from that daily candle?” The intraday report can narrow the exercise to the first hour. Keep both paths explicitly hypothetical unless timestamps are independently verified.
