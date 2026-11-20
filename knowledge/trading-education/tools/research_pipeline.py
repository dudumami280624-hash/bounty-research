#!/usr/bin/env python3
"""Source-grounded research pipeline. No claim is marked verified without review evidence.
Local outputs contain source excerpts and MUST NOT be committed to a public repository.
Optional OPENAI_API_KEY enables chart/page vision and draft claim analysis.
"""
import argparse, base64, hashlib, json, os, re, urllib.request
from pathlib import Path

def call_model(messages, model='gpt-4.1', max_tokens=3000):
    key=os.environ.get('OPENAI_API_KEY')
    if not key: raise RuntimeError('OPENAI_API_KEY is required for model analysis')
    body=json.dumps({'model':model,'messages':messages,'temperature':0,'max_tokens':max_tokens}).encode()
    req=urllib.request.Request('https://api.openai.com/v1/chat/completions',data=body,
      headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=180) as response:
        obj=json.load(response)
    return obj['choices'][0]['message']['content']

def vision_pdf(path, output, pages=None):
    import fitz
    doc=fitz.open(path); output=Path(output);output.mkdir(parents=True,exist_ok=True)
    results=[]
    for i in (pages if pages is not None else range(len(doc))):
        if i<0 or i>=len(doc): raise ValueError('Page out of range')
        page=doc[i]; png=page.get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False).tobytes('png')
        sha=hashlib.sha256(png).hexdigest()
        prompt=('Inspect this exact textbook page. Describe each visible candlestick/price-action chart: '
          'candle bodies and wicks, direction, trend context, axes, volume if visible, labels, '
          'confirmation conditions and uncertainty. Do not infer unreadable values or validate profitability. '
          'Return JSON with keys page, charts (array of objects), uncertain_details (array), '
          'requires_human_review (boolean). This is visual observation, not independent fact-checking.')
        raw=call_model([{'role':'user','content':[{'type':'text','text':prompt},
          {'type':'image_url','image_url':{'url':'data:image/png;base64,'+base64.b64encode(png).decode()}}]}])
        record={'page':i+1,'image_sha256':sha,'model_output':raw,
          'status':'ai_visual_observation_unverified','human_review_complete':False}
        (output/f'page-{i+1:04}.json').write_text(json.dumps(record,ensure_ascii=False,indent=2))
        results.append(record)
    return results

def research_claim(claim, source_sha, source_location, output, model='gpt-4.1'):
    """Independent web-supported research, explicitly pending human approval."""
    key=os.environ.get('OPENAI_API_KEY')
    if not key: raise RuntimeError('OPENAI_API_KEY is required for independent research')
    request_text=('Investigate this trading-education claim against independent primary or '
      'reputable references. Separate accepted definitions from empirical performance claims. '
      'Identify counterexamples, uncertainty and verifiable source URLs. Do not assume a '
      'textbook statement is correct. Return a concise report with citations. Claim: '+claim)
    body=json.dumps({'model':model,'tools':[{'type':'web_search_preview'}],
      'input':request_text}).encode()
    req=urllib.request.Request('https://api.openai.com/v1/responses',data=body,
      headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'})
    with urllib.request.urlopen(req,timeout=180) as response: result=json.load(response)
    record={'claim':claim,'source_sha':source_sha,'source_location':source_location,
      'independent_research_response':result.get('output',[]),
      'status':'research_complete_human_review_pending',
      'verified':False,'reviewer_approved':False}
    dest=Path(output);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\\n')
    return record

def build_knowledge(evidence_dir, output):
    evidence_dir=Path(evidence_dir);by_topic={}
    for p in sorted(evidence_dir.glob('*.json')):
        obj=json.loads(p.read_text())
        for topic in obj.get('topics',[]):
            name=topic.get('concept')
            if not name: continue
            by_topic.setdefault(name,[]).append({'source_sha':obj.get('source_sha'),
              'source_name':obj.get('source_name'),'locations':topic.get('evidence_locations',[]),
              'status':'candidate_unverified'})
    result={'schema_version':1,'topics':{},'verified_claims':0,
      'notice':'Keyword mentions are NOT facts. No contradictions resolved or claims verified.'}
    for topic,items in sorted(by_topic.items()):
        unique={x['source_sha']:x for x in items if x['source_sha']}
        result['topics'][topic]={'sources':list(unique.values()),'claims':[],
          'status':'needs_independent_fact_check','contradictions_resolved':False}
    Path(output).parent.mkdir(parents=True,exist_ok=True)
    Path(output).write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n')
    return result

def draft_lesson(topic, catalog, out, research_dir=None):
    data=json.loads(Path(catalog).read_text())
    item=data['topics'].get(topic)
    if not item: raise ValueError('Topic not in evidence catalog')
    claims=[c for c in item['claims'] if c.get('status')=='verified'
      and c.get('independent_reference') and c.get('source_sha')]
    if not claims: raise RuntimeError('No independently verified source-linked claims; lesson publication blocked')
    context=json.dumps({'topic':topic,'verified_claims':claims},ensure_ascii=False)
    raw=call_model([{'role':'system','content':'Write an original English educational lesson using ONLY verified supplied claims. Explain limitations, risk and citations. Never promise returns. Do not copy textbooks.'},
      {'role':'user','content':context}])
    dest=Path(out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text('# '+topic.replace('_',' ').title()+'\n\n'+raw+'\n')
    return dest

def main():
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest='cmd',required=True)
    v=sub.add_parser('vision');v.add_argument('pdf');v.add_argument('--out',required=True);v.add_argument('--pages',type=int,nargs='*')
    k=sub.add_parser('catalog');k.add_argument('evidence_dir');k.add_argument('--out',required=True)
    q=sub.add_parser('fact-check');q.add_argument('claim');q.add_argument('--sha',required=True);q.add_argument('--location',required=True);q.add_argument('--out',required=True)
    d=sub.add_parser('lesson');d.add_argument('topic');d.add_argument('catalog');d.add_argument('--out',required=True)
    a=p.parse_args()
    if a.cmd=='vision':print(json.dumps({'pages_analyzed':len(vision_pdf(a.pdf,a.out,([x-1 for x in a.pages] if a.pages else None)))}))
    elif a.cmd=='fact-check':
        r=research_claim(a.claim,a.sha,a.location,a.out)
        print(json.dumps({'status':r['status'],'verified':r['verified']}))
    elif a.cmd=='catalog':
        r=build_knowledge(a.evidence_dir,a.out)
        print(json.dumps({'topics':len(r['topics']),'verified_claims':r['verified_claims']}))
    else:print(draft_lesson(a.topic,a.catalog,a.out))
if __name__=='__main__':main()
