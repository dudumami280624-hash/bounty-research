"""Compare US weekly/monthly candle signals to same-stock trend controls."""
import argparse
import calendar
import hashlib
import json
import math
from collections import defaultdict
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from statistics import mean, median

FRAME = {"weekly": ((4, 13, 26), (13, 26, 52)),
         "monthly": ((1, 3, 6), (3, 6, 12))}
DIRECTIONS = {1: "hammer", -1: "shooting_star"}
HOLDOUT = date(2016, 1, 1)


def period_end(day, frame):
    if frame == "weekly":
        return day + timedelta(days=4 - day.weekday())
    return day.replace(day=calendar.monthrange(day.year, day.month)[1])


def read_bars(path, frame, cutoff):
    data = json.loads(path.read_bytes())["chart"]["result"][0]
    q = data["indicators"]["quote"][0]
    daily = {}
    bad_count = 0
    for ts, *prices in zip(data["timestamp"], *(q[k] for k in ("open", "high", "low", "close")), strict=True):
        day = datetime.fromtimestamp(ts, timezone.utc).date()
        if day.weekday() >= 5 or period_end(day, frame) >= cutoff:
            continue
        if not all(v is not None and math.isfinite(v) and v > 0 for v in prices):
            bad_count += 1
            continue
        o, h, l, c = prices
        if l > min(o, c) or h < max(o, c) or day in daily:
            bad_count += 1
            continue
        daily[day] = (o, h, l, c)
    groups = defaultdict(list)
    for day, prices in sorted(daily.items()):
        groups[period_end(day, frame)].append(prices)
    bars = [(d, q[0][0], max(v[1] for v in q), min(v[2] for v in q), q[-1][3])
            for d, q in sorted(groups.items())]
    return bars[1:], bad_count


def observation(bars, i, lookbacks, horizons):
    day, o, h, l, c = bars[i]
    changes = tuple(math.log(bars[i-1][4] / bars[i-j-1][4]) for j in lookbacks)
    if min(changes) > 0:
        direction = -1
    elif max(changes) < 0:
        direction = 1
    else:
        return None
    body = abs(c-o)
    span = h-l
    upper, lower = h-max(o,c), min(o,c)-l
    dominant, other = (lower, upper) if direction == 1 else (upper, lower)
    signal = 0 < body <= 0.35*span and dominant >= 2*body and other <= 0.15*span
    entry = bars[i+1][1]
    returns = tuple(direction*(bars[i+h][4]/entry-1) for h in horizons)
    return (day, changes, direction, signal, returns)


def compare(paths, frame, cutoff):
    lookbacks, horizons = FRAME[frame]
    outcomes = defaultdict(list)
    examples = defaultdict(list)
    source_stats = {}
    for p in paths:
        bars, bad = read_bars(p, frame, cutoff)
        source_stats[p.stem] = {"bars":len(bars), "excluded_invalid_daily_rows":bad,
                               "last_bar":bars[-1][0].isoformat() if bars else None}
        obs = [v for i in range(max(lookbacks)+1, len(bars)-max(horizons))
               if (v := observation(bars,i,lookbacks,horizons))]
        for side in DIRECTIONS:
            for era in ("pre2016","2016plus"):
                sample = [o for o in obs if o[2] == side and
                          ((o[0] >= HOLDOUT) == (era == "2016plus"))]
                controls = {i:o for i,o in enumerate(sample) if not o[3]}
                signals = [o for o in sample if o[3]]
                matched = []
                for signal in signals:
                    d, moves, _, _, returns = signal
                    eligible = ((i,v) for i,v in controls.items() if abs((v[0]-d).days) <= 730)
                    match = min(eligible, key=lambda iv: (sum(abs(a-b) for a,b in zip(moves,iv[1][1])),
                                                          abs((d-iv[1][0]).days)), default=None)
                    if match is None:
                        continue
                    i, control = match
                    del controls[i]
                    matched.append((returns, control[4]))
                    if p.stem in {"NKE","DAL","SPY"} and era=="2016plus":
                        examples[(side,era)].append({"ticker":p.stem,"signal":str(d),"control":str(control[0]),
                                                    "signed_returns":returns,"control_signed_returns":control[4]})
                outcomes[side,era].append((len(signals),matched))
    results = []
    for (side, era), rows in sorted(outcomes.items()):
        pairs = [p for _,m in rows for p in m]
        metrics = []
        for j,n in enumerate(horizons):
            if not pairs:
                continue
            hits = sum(s[j] > 0 for s,c in pairs)
            control_hits = sum(c[j] > 0 for s,c in pairs)
            diffs = [(int(s[j]>0)-int(c[j]>0))*100 for s,c in pairs]
            per_stock = [mean((int(s[j]>0)-int(c[j]>0))*100 for s,c in matched)
                         for _,matched in rows if matched]
            metrics.append({"horizon":n,"signal_hits":hits,"control_hits":control_hits,
                            "hit_rate_delta_pp":round(mean(diffs),3),
                            "equal_weight_ticker_delta_pp":round(mean(per_stock),3),
                            "median_signed_return_difference_pp":round(median((s[j]-c[j])*100 for s,c in pairs),3)})
        results.append({"pattern":DIRECTIONS[side],"period":era,
                        "eligible_signals":sum(n for n,_ in rows),"matched_pairs":len(pairs),
                        "tickers_with_matches":sum(bool(m) for _,m in rows),"metrics":metrics,
                        "examples":examples[side,era]})
    return {"asset_histories":len(paths),"results":results,"source_stats":source_stats}


if __name__ == "__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("data",type=Path)
    parser.add_argument("--cutoff",type=date.fromisoformat,required=True)
    args=parser.parse_args()
    files=sorted(args.data.glob("*.json"))
    if not files:
        parser.error("no source JSON files")
    print(json.dumps({frame:compare(files,frame,args.cutoff) for frame in FRAME},indent=2))
