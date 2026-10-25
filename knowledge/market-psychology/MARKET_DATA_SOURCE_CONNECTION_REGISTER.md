# Market Data Source Connection Register v0.1

| Layer | Selected source | Coverage | Status |
|---|---|---|---|
| Daily volume | Nasdaq Historical Data / Nasdaq Data Link Bars | Up to 10 years daily OHLCV for U.S. equities | SOURCE IDENTIFIED; API/download access pending |
| Bid/ask quote | Polygon or Tiingo | Provider-dependent historical quotes | NOT CONNECTED |
| Trade/order flow | Databento or Nasdaq TotalView/ITCH/TAQ | Tick/order-book data | NOT CONNECTED |
| Causal controls | FRED / Federal Reserve / BLS | Rates, CPI, employment, policy dates | AVAILABLE |

Official Nasdaq historical page: https://www.nasdaq.com/market-activity/quotes/historical
Nasdaq Data Link API: https://www.nasdaq.com/products/data/data-link/api

The Nasdaq page states that historical data provides up to ten years of daily prices and volumes. Nasdaq TotalView is a separate order-book feed and cannot be inferred from daily candles.
