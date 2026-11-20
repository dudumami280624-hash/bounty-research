#!/usr/bin/env python3
"""Extract the next original source in the 178-file inventory.
Outputs only non-copyrighted processing metadata to the public repository.
Never marks image review, factual validation, or teaching integration as complete.
"""
import base64, hashlib, json, os, re, sys, tempfile, urllib.request, subprocess, shutil, time
from datetime import datetime, timezone
from pathlib import Path
from extract_source import ooxml, pdf
from evidence_candidates import candidates
from free_visual import inspect_pdf
from free_research import make_packet, draft

ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/'integration/source-inventory-178-2026-11-20.md'
STATE=ROOT/'integration/extraction-state.json'
REPORT=ROOT/'integration/latest-extraction-report.md'
REPO=os.environ.get('GITHUB_REPOSITORY','dudumami280624-hash/bounty-research')
TOKEN=os.environ.get('GITHUB_TOKEN','')
MAX_ATTEMPTS=3
BATCH_SIZE=max(1,min(12,int(os.environ.get('TMM_BATCH_SIZE','4'))))

def inventory(text):
    section=''; entries=[]
    for line in text.splitlines():
        if line.startswith('## '): section=line[3:].strip()
        match=re.match(r'^- `([^`]+)` .*?Git blob SHA-1 `([0-9a-f]{40})`',line)
        if match: entries.append({'name':match.group(1),'sha':match.group(2),'category':section})
    if len(entries)!=178: raise ValueError(f'Expected 178 inventory entries, found {len(entries)}')
    entries.sort(key=lambda x:(not x['category'].startswith('01-'), not x['name'].lower().endswith('.pdf'), x['name']))
    return entries

def download_blob(sha):
    url=f'https://api.github.com/repos/{REPO}/git/blobs/{sha}'
    req=urllib.request.Request(url,headers={
        'Authorization':f'Bearer {TOKEN}',
        'Accept':'application/vnd.github+json',
        'X-GitHub-Api-Version':'2022-11-28'})
    with urllib.request.urlopen(req,timeout=180) as response: data=json.load(response)
    if data.get('encoding')!='base64': raise ValueError('Blob was not returned as base64')
    blob=base64.b64decode(data['content'],validate=False)
    actual=hashlib.sha1(b'blob '+str(len(blob)).encode()+b'\0'+blob).hexdigest()
    if actual!=sha: raise ValueError('Git blob checksum mismatch')
    if blob.startswith(b'version https://git-lfs.github.com/spec/v1'):
        raise ValueError('Git LFS pointer requires separate authenticated LFS download')
    return blob

def extract(entry, blob):
    ext=Path(entry['name']).suffix.lower()
    if ext not in ('.pdf','.docx','.pptx','.doc','.ppt'):
        return {'extraction_status':'needs_conversion','reason':f'Unsupported extension {ext}'}
    with tempfile.TemporaryDirectory() as temp:
        source=Path(temp)/('source'+ext)
        source.write_bytes(blob)
        if ext in ('.doc','.ppt'):
            if not shutil.which('libreoffice'):
                return {'extraction_status':'needs_conversion','reason':'LibreOffice not installed'}
            target_ext='.docx' if ext=='.doc' else '.pptx'
            converted=Path(temp)/('source'+target_ext)
            profile=Path(temp)/'lo-profile'
            proc=subprocess.run(['libreoffice','-env:UserInstallation=file://'+str(profile),
              '--headless','--convert-to',target_ext[1:],'--outdir',temp,str(source)],
              capture_output=True,text=True,timeout=180)
            if proc.returncode!=0 or not converted.exists():
                raise RuntimeError('LibreOffice conversion failed: '+proc.stderr[-200:])
            source=converted;ext=target_ext
        blocks,images,details=(pdf(source) if ext=='.pdf' else ooxml(source,ext[1:]))
        # Temporary private working files only; do not publish or upload artifacts.
        work=Path(os.environ.get('RUNNER_TEMP',temp))/'tmm-private-extraction'/entry['sha']
        work.mkdir(parents=True,exist_ok=True)
        (work/'extracted_text.md').write_text('\n\n'.join(
            f"### {b['location']}\n{b['text']}" for b in blocks),encoding='utf-8')
        (work/'image_inventory.json').write_text(json.dumps(images,ensure_ascii=False,indent=2),encoding='utf-8')
        packet=make_packet(blocks,entry['sha'],entry['name'])
        packet_dir=work/'private-research'/entry['sha']
        packet_dir.mkdir(parents=True,exist_ok=True)
        (packet_dir/'evidence-packet.json').write_text(json.dumps(packet,ensure_ascii=False,indent=2),encoding='utf-8')
        for topic in packet['topics']:
            (packet_dir/(topic+'-research-draft.md')).write_text(draft(packet,topic),encoding='utf-8')
        vision_result={'status':'not_applicable','pages_analyzed':0}
        if ext=='.pdf':
            try:
                observations=inspect_pdf(source,work/'visual-review'/entry['sha'])
                vision_result={'status':'free_visual_features_unverified',
                  'pages_analyzed':len(observations),
                  'chart_candidate_pages':sum(bool(x.get('chart_candidate')) for x in observations),
                  'ocr_failed_pages':sum(not x.get('ocr_success',False) for x in observations)}
            except Exception as exc:
                vision_result={'status':'free_visual_failed','pages_analyzed':0,
                  'error':str(exc)[:300]}
        if vision_result.get('ocr_failed_pages',0):
            details['ocr_failed_pages']=vision_result['ocr_failed_pages']
        evidence=ROOT/'integration/evidence-index'/ (entry['sha']+'.json')
        evidence.parent.mkdir(parents=True,exist_ok=True)
        evidence.write_text(json.dumps({'source_sha':entry['sha'],'source_name':entry['name'],
          'topics':candidates(blocks),'chart_verified':False,'fact_checked':False,
          'lesson_integrated':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return {'extraction_status':('partial_ocr_failure' if details.get('ocr_failed_pages') else ('extracted' if blocks else 'needs_visual_review')),
            'source_sha256':hashlib.sha256(blob).hexdigest(),
            'text_blocks':len(blocks),'images_found':len(images),'topic_candidates':len(candidates(blocks)),'private_research_topics':len(packet['topics']),
            'research_draft_status':'internal_unverified_only','details':details,'visual_ai':vision_result}

def main():
    if not TOKEN: raise RuntimeError('GITHUB_TOKEN is missing')
    entries=inventory(INDEX.read_text(encoding='utf-8'))
    state=json.loads(STATE.read_text(encoding='utf-8')) if STATE.exists() else {'schema_version':2,'files':{}}
    files=state.setdefault('files',{})
    terminal={'extracted','needs_visual_review'}
    converter_available=bool(shutil.which('libreoffice'))
    pending=[e for e in entries if files.get(e['sha'],{}).get('extraction_status') not in terminal
             and (files.get(e['sha'],{}).get('attempts',0)<MAX_ATTEMPTS
                  or (files.get(e['sha'],{}).get('extraction_status')=='needs_conversion' and converter_available))
             and (converter_available or Path(e['name']).suffix.lower() not in ('.doc','.ppt'))]
    processed=[]
    started=time.monotonic()
    budget_seconds=max(60,int(os.environ.get('TMM_TIME_BUDGET_SECONDS','1050')))
    for entry in pending[:BATCH_SIZE]:
        if time.monotonic()-started>=budget_seconds:
            print('Batch time budget reached; remaining files will resume next run',flush=True)
            break
        sha=entry['sha'];previous=files.get(sha,{})
        attempts=previous.get('attempts',0)+1
        try: status=extract(entry,download_blob(sha))
        except Exception as exc: status={'extraction_status':'failed','error':str(exc)[:500]}
        status.update({'source_name':entry['name'],'category':entry['category'],
                       'attempts':attempts,'last_attempt_utc':datetime.now(timezone.utc).isoformat(),
                       'visual_review_complete':False,'fact_checked':False,
                       'integrated_into_lesson':False})
        files[sha]=status
        # Persist a checkpoint after every source, before the next slow download/OCR.
        STATE.parent.mkdir(parents=True,exist_ok=True)
        checkpoint=STATE.with_suffix('.json.tmp')
        checkpoint.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        checkpoint.replace(STATE)
        processed.append({'source_name':entry['name'],'source_sha':sha,'status':status['extraction_status']})
    status=files[processed[-1]['source_sha']] if processed else {'extraction_status':'no_eligible_files'}
    state['schema_version']=2
    STATE.parent.mkdir(parents=True,exist_ok=True)
    STATE.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    counts={s:sum(v.get('extraction_status')==s for v in files.values())
            for s in ('extracted','partial_ocr_failure','needs_visual_review','needs_conversion','failed')}
    exhausted=sum(v.get('extraction_status')=='failed' and v.get('attempts',0)>=MAX_ATTEMPTS
                  for v in files.values())
    reviewed=sum(bool(v.get('visual_review_complete')) for v in files.values())
    checked=sum(bool(v.get('fact_checked')) for v in files.values())
    integrated=sum(bool(v.get('integrated_into_lesson')) for v in files.values())
    REPORT.write_text('# The Market Mind — 178份原件自动处理进度\n\n'
       +f'- 本轮批量处理：{len(processed)}份\n'
       +''.join(f'- {x["source_name"]}：{x["status"]}\n' for x in processed)
       +f'- 本轮状态：{status["extraction_status"]}\n'
       +f'- 已提取文字：{counts["extracted"]}/178\n'
       +f'- OCR不完整待重试：{counts["partial_ocr_failure"]}\n'
       +f'- 需视觉复核：{counts["needs_visual_review"]}\n'
       +f'- 需旧格式转换：{counts["needs_conversion"]}\n'
       +f'- 失败待重试：{counts["failed"]-exhausted}；重试耗尽：{exhausted}\n'
       +f'- 完成图表视觉核验：{reviewed}；完成事实核验：{checked}；完成课程融合：{integrated}\n\n'
       +'**提取文字不代表理解或核验。** 原件和提取全文不提交到公开仓库。\n',encoding='utf-8')
    print(json.dumps({'processed':processed,'counts':counts},ensure_ascii=False))
    # Record individual failures and continue; a single bad source must not block progress.

if __name__=='__main__': main()
