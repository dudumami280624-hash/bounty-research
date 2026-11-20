#!/usr/bin/env python3
"""Generate source-linked topic *candidates*; never assert fact verification.
Writes only counts, locations and original-source checksums, not copied text.
"""
import json, re, sys
from pathlib import Path

TERMS={
 'candlestick':['candlestick','蜡烛图','k线','k 线','k-line'],
 'doji':['doji','十字星','十字线'],
 'engulfing':['engulfing','吞没','吞噬'],
 'hammer':['hammer','锤子线','锤头线'],
 'trend':['trend','趋势','上升趋势','下降趋势'],
 'support_resistance':['support','resistance','支撑','阻力','压力位'],
 'volume':['volume','成交量','量能'],
 'risk':['risk','止损','风险','回撤','stop loss'],
 'moving_average':['moving average','均线','移动平均线'],
 'confirmation':['confirmation','确认','假突破','false breakout']
}
def candidates(blocks):
    result=[]
    for concept,variants in TERMS.items():
        hits=[]
        for b in blocks:
            text=b.get('text','').casefold()
            count=sum(text.count(term.casefold()) for term in variants)
            if count: hits.append({'location':b['location'],'term_mentions':count})
        if hits: result.append({'concept':concept,'mentions':sum(h['term_mentions'] for h in hits),
                                'evidence_locations':hits[:60],'status':'candidate_unverified'})
    return result

def main():
    src=Path(sys.argv[1]);dest=Path(sys.argv[2]);sha=sys.argv[3];name=sys.argv[4]
    blocks=json.loads(src.read_text(encoding='utf-8'))
    obj={'source_sha':sha,'source_name':name,'evidence_type':'term-location-index',
         'claim_verified':False,'chart_verified':False,'independent_source_checked':False,
         'lesson_integrated':False,'topics':candidates(blocks)}
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(obj,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f"Generated {len(obj['topics'])} unverified topic candidates")
if __name__=='__main__':main()
