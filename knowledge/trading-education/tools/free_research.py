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
    """Private, passage-based teaching worksheet; never a verified public lesson."""
    entries=packet['topics'].get(topic,[])
    if not entries: raise ValueError('No source passages for requested topic')
    lines=['# '+topic.replace('_',' ').title()+' — Source-Based Teaching Worksheet',
      'INTERNAL UNVERIFIED DRAFT — NOT FOR PUBLICATION',
      '## Learning objective',
      'Examine how the supplied textbook describes '+topic.replace('_',' ')+
      ', identify the conditions under which its examples apply, and distinguish observation from prediction.',
      '## Textbook passages and teaching notes']
    for i,item in enumerate(entries[:12],1):
        passage=item.get('excerpt','').strip()
        lines.extend(['### Passage '+str(i)+' — '+str(item['location']),
          'Source excerpt (private, not for republication):',
          '> '+passage.replace('\\n',' ').replace('\\r',' ')[:900],
          'Evidence fingerprint: '+item['excerpt_sha256'],
          'Teaching analysis: What does this passage explicitly define or describe? '
          'What observable conditions, exceptions, and chart details are present? '
          'Do not assume an outcome the passage does not establish.'])
    lines+=['## Worked analysis exercise',
      '1. Identify the chart context and any explicitly stated entry, confirmation, or invalidation condition.',
      '2. Separate the source author\'s interpretation from visible market observations.',
      '3. Explain one plausible alternative reading and what evidence would distinguish it.',
      '4. Describe risks and uncertainty without claiming a guaranteed trading outcome.',
      '## Cross-source synthesis',
      'Compare definitions and examples with other source passages before consolidating a lesson.',
      '## Verification checklist',
      '- Compare each substantive claim against an independent primary or reputable reference.',
      '- Inspect original charts; OCR and image counts do not establish chart meaning.',
      '- Record counterexamples, uncertainty, and disagreements.',
      '- Do not publish until teaching claims and visual examples have been reviewed.']
    return '\\n\\n'.join(lines)+'\\n'

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
