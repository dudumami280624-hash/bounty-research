# US Historical Data Register v0.2

## Primary series

| Case | Market | Macro | Credit / system | Source |
|---|---|---|---|---|
| 1929–32 | Dow-Jones historical index | industrial production, prices | national-bank suspensions, business failures | FRED Macrohistory / NBER |
| 1970s | S&P 500 | CPIAUCSL, UNRATE, FEDFUNDS | oil shock and policy regime | FRED / Federal Reserve History |
| 1987 | SP500, NASDAQCOM | FEDFUNDS | volume, order imbalance, circuit-breaker record | FRED / SEC |
| 2000 | NASDAQCOM, SP500 | CPIAUCSL, FEDFUNDS | valuation, earnings and issuance measures | FRED / NBER |
| 2001–09 | SP500 | FEDFUNDS, GDP, unemployment | USSTHPI, DRSFRMACBS, mortgage liabilities | FRED / Federal Reserve |
| 2020 | SP500 | unemployment, rates, CPI | credit spreads and liquidity measures | FRED / Federal Reserve |
| 2022 | SP500, NASDAQCOM | CPIAUCSL, FEDFUNDS, Treasury yields | credit spreads and financial conditions | FRED / Federal Reserve |

## Rules

- Record vintage/retrieval date and transformation.
- Do not mix daily market data with quarterly credit data without declaring aggregation.
- Preserve missing values and revisions.
- Data supports a claim only after a counterexample and an out-of-sample test are recorded.
