"""Count unique signal dates, including cross-timeframe duplicates."""
import hashlib
import json
from datetime import date, datetime, timezone
from pathlib import Path

from analyze import FRAME, observation, period_end, read_bars

root = Path(__file__).resolve().parent
cutoff = date(2026, 11, 25)
requested = json.loads((root/"fetch-results.json").read_text())
unique = set()
timeframe_events = 0
manifest = []
for ticker, status in requested:
    path = root / "data" / f"{ticker}.json"
    if not path.exists():
        manifest.append({"ticker": ticker, "error": status})
        continue
    buf = path.read_bytes()
    series = json.loads(buf)["chart"]["result"][0]["timestamp"]
    manifest.append({"ticker": ticker, "sha256": hashlib.sha256(buf).hexdigest(),
                     "raw_date_rows": len(series)})
    trading_days = [datetime.fromtimestamp(s,timezone.utc).date() for s in series]
    for frame, (prior, forward) in FRAME.items():
        last_session = {period_end(day,frame):day for day in trading_days if day.weekday()<5}
        bars, _ = read_bars(path,frame,cutoff)
        for i in range(max(prior)+1,len(bars)-max(forward)):
            event = observation(bars,i,prior,forward)
            if event and event[3]:
                unique.add((ticker,last_session[event[0]]))
                timeframe_events += 1
print("assets",sum("sha256" in x for x in manifest),"raw",sum(x.get("raw_date_rows",0) for x in manifest),
      "eligible",timeframe_events,"unique_ticker_session",len(unique))
artifact = {"roster_sha256": hashlib.sha256((root/"constituents.csv").read_bytes()).hexdigest(),
            "exchange_directory_sha256": hashlib.sha256((root/"otherlisted.txt").read_bytes()).hexdigest(),
            "cutoff":str(cutoff),"eligible_events":timeframe_events,
            "unique_ticker_sessions":len(unique),"sources":manifest}
(root/"manifest.json").write_text(json.dumps(artifact,indent=2)+"\n")
