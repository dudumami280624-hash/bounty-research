import csv
import io
import json
import hashlib
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote
from urllib.request import Request, urlopen

base=Path(__file__).resolve().parent
constituents='https://raw.githubusercontent.com/datasets/s-and-p-500-companies/main/data/constituents.csv'
def get(url):
    with urlopen(Request(url, headers={'User-Agent':'Mozilla/5.0'}),timeout=13) as r:
        return r.read()
roster = base / 'constituents.csv'
raw = roster.read_bytes() if roster.exists() else get(constituents)
roster.write_bytes(raw)
(base / 'data').mkdir(exist_ok=True)
universe={row['Symbol'].replace('.','-') for row in csv.DictReader(io.StringIO(raw.decode('utf-8-sig')))}
directory_url = "https://www.nasdaqtrader.com/dynamic/SymDir/otherlisted.txt"
directory = base / "otherlisted.txt"
directory_raw = directory.read_bytes() if directory.exists() else get(directory_url)
directory.write_bytes(directory_raw)
additional = set()
for row in csv.DictReader(io.StringIO(directory_raw.decode("utf-8-sig")), delimiter="|"):
    ticker = row["ACT Symbol"]
    name = (row.get("Security Name") or "").lower()
    if (ticker not in universe and re.fullmatch(r"[A-Z]{1,4}", ticker)
        and row.get("Exchange") == "N" and row.get("ETF") == "N"
        and row.get("Test Issue") == "N" and "common stock" in name):
        additional.add(ticker)
extension = sorted(additional, key=lambda t: hashlib.sha256(
    ("US-weekly-monthly-2026-11-25:" + t).encode()).digest())[:100]
symbols = list(dict.fromkeys(["SPY", "NKE", "DAL"] + sorted(universe) + extension))
(base / "nyse-extension.json").write_text(json.dumps(extension))
def epoch(y, m, d):
    return int(datetime(y, m, d, tzinfo=timezone.utc).timestamp())

start,end=epoch(1990,1,1),epoch(2026,11,25)
def fetch(s):
    file=base/'data'/f'{s}.json'
    if file.exists(): return (s,'cached')
    errors=[]
    for host in ['query1.finance.yahoo.com','query2.finance.yahoo.com']:
        try:
            url=f'https://{host}/v8/finance/chart/{quote(s)}?period1={start}&period2={end}&interval=1d&includePrePost=false&events=splits'
            response=get(url)
            d=json.loads(response)['chart']['result'][0]
            timestamps=d['timestamp']
            if len(timestamps)<200 or d['meta']['symbol']!=s or d['meta']['currency']!='USD': raise ValueError('invalid symbol, currency or history')
            file.write_bytes(response)
            return (s,len(timestamps))
        except Exception as e: errors.append(str(e))
    return(s,' | '.join(errors))
with ThreadPoolExecutor(max_workers=24) as pool:
    results=list(pool.map(fetch,symbols))
(base/'fetch-results.json').write_text(json.dumps(results))
print(len(symbols),'requested;',sum(isinstance(v,int) or v=='cached' for _,v in results),'available',flush=True)
print([r for r in results if not isinstance(r[1],int) and r[1]!='cached'][:20],flush=True)
