# SPY exploratory candle event study — 2026-11-25
Source: https://github.com/OStochastic/Daily-SPY-data-from-2000-2025/blob/main/spy_data.csv ; fetched blob fd424789a7547730397e755c417de34caf9cedac. 6454 dated rows, 2000-01-03 through 2025-08-29. Third-party price series; independent vendor reconciliation pending. Prices appear adjusted; exact adjustment policy pending.
Method executed in JavaScript: sort by date; i=5 through n-6; body=abs(C-O)>0; range=H-L>0; body/range<=0.35; trend=C[i-1]/C[i-5]-1. Hammer: trend<-0.01, lower wick>=2*body and upper wick<=0.15*range. Star: trend>0.01, upper wick>=2*body and lower wick<=0.15*range. Return=C[i+5]/O[i+1]-1. Correct direction: positive for hammer, negative for star. No cost, stop, benchmark or significance test; overlapping events permitted.
Results: hammer 73, 43 correct, mean underlying return +0.293754%; star 53, 34 correct, mean underlying return -0.157540%. Direction frequencies not strategy win rates.
Examples (date,O,H,L,C,volume,return):
2000-05-22,89.716973,89.855915,87.017524,88.962715,10839400,+1.468667% hammer support
2000-02-14,88.558993,88.558993,87.628460,88.380806,8528800,-3.074566% hammer counterexample
2001-07-31,77.895731,78.977258,77.766979,78.121048,11918100,-0.983821% star support
2001-09-28,66.543834,70.834482,66.233664,67.487259,21687200,+3.204996% star counterexample
Disposition: retain textbook context insight. Exploratory evidence only; benchmark, matched controls, volume stratification, robustness and independent data checks remain. Does not verify original NKE/DAL charts. Original sources unchanged.
