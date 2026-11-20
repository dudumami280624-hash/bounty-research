#!/usr/bin/env python3
"""Free, offline evidence-to-draft bridge. All claims remain unverified.
Private research packets must never be committed to the public repository.
"""
import argparse, hashlib, json, re
from pathlib import Path
from evidence_candidates import TERMS

def make_packet(blocks, source_sha, source_name):
    topics={}
    for block in blocks:
        location=block['location'];text=block.get('text','').strip()
        if not text: continue
        for topic,terms in TERMS.items():
            if any(t.casefold() in text.casefold() for t in terms):
                record={'source_sha':source_sha,'location':location,
                  'excerpt_sha256':hashlib.sha256(text.encode()).hexdigest(),
                  'excerpt':text[:900],'status':'unverified_source_statement'}
                topics.setdefault(topic,[]).append(record)
    return {'source_sha':source_sha,'source_name':source_name,
      'topics':topics,'status':'private_unverified_research_packet'}

def draft(packet, topic):
    entries=packet['topics'].get(topic,[])
    if not entries: raise ValueError('No source passages for requested topic')
    lines=['# '+topic.replace('_',' ').title()+' — Research Draft',
      'INTERNAL UNVERIFIED DRAFT — NOT FOR PUBLICATION',
      '## Source-backed questions (not verified claims)']
    for item in entries[:12]:
        lines.append('- Examine source passage at '+item['location']+
          ' (SHA256 '+item['excerpt_sha256'][:16]+'). What does it define, what evidence supports it, and what are its limitations?')
    lines+=['## Verification checklist',
      '- Compare the definition against an independent primary or reputable reference.',
      '- Inspect original charts; OCR and image counts do not establish chart meaning.',
      '- Record counterexamples and avoid profitability promises.',
      '- Do not publish until every teaching claim has a cited and reviewed reference.']
    return '\n\n'.join(lines)+'\n'

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('blocks_json');parser.add_argument('--sha',required=True)
    parser.add_argument('--name',required=True);parser.add_argument('--out',required=True)
    parser.add_argument('--draft-topic');args=parser.parse_args()
    blocks=json.loads(Path(args.blocks_json).read_text(encoding='utf-8'))
    packet=make_packet(blocks,args.sha,args.name)
    dest=Path(args.out);dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_text(json.dumps(packet,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    if args.draft_topic:
        dest.with_suffix('.md').write_text(draft(packet,args.draft_topic),encoding='utf-8')
    print(json.dumps({'topics':len(packet['topics']),'status':packet['status']}))
if __name__=='__main__':main()
