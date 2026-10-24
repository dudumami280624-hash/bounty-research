# 美国历史验证数据包规范

## 数据系列

- S&P 500：FRED `SP500`
- Nasdaq Composite：FRED `NASDAQCOM`
- Federal Funds Rate：FRED `FEDFUNDS`
- CPI：FRED `CPIAUCSL`
- Unemployment：FRED `UNRATE`
- 10Y Treasury：FRED `DGS10`
- 2Y Treasury：FRED `DGS2`
- 10Y–2Y spread：FRED `T10Y2Y`
- VIX / volatility：CBOE or FRED series
- Margin debt：FINRA monthly margin statistics
- Recession dates：NBER business-cycle chronology

## Historical windows

1929–1932, 1968–1982, 1997–2002, 2007–2009, February–April 2020, and 2022 tightening cycle.

## Required fields

Each imported dataset must record source URL, series ID, observation frequency, timezone, retrieval date, units, revisions policy, missing values, and license/usage notes.

## Validation rules

- Use point-in-time data where possible.
- Never use revised data to claim a trader could have known the final number at the time.
- Compare price, rates, inflation, credit and breadth together.
- Include at least one false signal and one period where the framework was uncertain.
- Save raw data separately from cleaned data and calculations.

## Status

This file defines the package. Actual downloads and derived tables must be added with source metadata and hashes before being used as evidence.