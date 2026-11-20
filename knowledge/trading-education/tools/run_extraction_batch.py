#!/usr/bin/env python3
"""Extract the next original source in the 178-file inventory.
Outputs only non-copyrighted processing metadata to the public repository.
Never marks image review, factual validation, or teaching integration as complete.
"""
import base64, hashlib, json, os, re, sys, tempfile, urllib.request
from datetime import datetime, timezone
from pathlib import Path
from extract_source import ooxml, pdf
from evidence_candidates import candidates

ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/'integration/source-inventory-178-2026-11-20.md'
STATE=ROOT/'integration/extraction-state.json'
REPORT=ROOT/'integration/latest-extraction-report.md'
REPO=os.environ.get('GITHUB_REPOSITORY','dudumami280624-hash/bounty-research')
TOKEN=os.environ.get('GITHUB_TOKEN','')
MAX_ATTEMPTS=3

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
    if ext not in ('.pdf','.docx','.pptx'):
        return {'extraction_status':'needs_conversion','reason':f'Legacy or unsupported extension {ext}'}
    with tempfile.TemporaryDirectory() as temp:
        source=Path(temp)/('source'+ext)
        source.write_bytes(blob)
        blocks,images,details=(pdf(source) if ext=='.pdf' else ooxml(source,ext[1:]))
        # Temporary private working files only; do not publish or upload artifacts.
        work=Path(os.environ.get('RUNNER_TEMP',temp))/'tmm-private-extraction'
        work.mkdir(parents=True,exist_ok=True)
        (work/'extracted_text.md').write_text('\n\n'.join(
            f"### {b['location']}\n{b['text']}" for b in blocks),encoding='utf-8')
        (work/'image_inventory.json').write_text(json.dumps(images,ensure_ascii=False,indent=2),encoding='utf-8')
        evidence=ROOT/'integration/evidence-index'/ (entry['sha']+'.json')
        evidence.parent.mkdir(parents=True,exist_ok=True)
        evidence.write_text(json.dumps({'source_sha':entry['sha'],'source_name':entry['name'],
          'topics':candidates(blocks),'chart_verified':False,'fact_checked':False,
          'lesson_integrated':False},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return {'extraction_status':'extracted' if blocks else 'needs_visual_review',
            'source_sha256':hashlib.sha256(blob).hexdigest(),
            'text_blocks':len(blocks),'images_found':len(images),'topic_candidates':len(candidates(blocks)),'details':details}

def main():
    if not TOKEN: raise RuntimeError('GITHUB_TOKEN is missing')
    entries=inventory(INDEX.read_text(encoding='utf-8'))
    state=json.loads(STATE.read_text(encoding='utf-8')) if STATE.exists() else {'schema_version':2,'files':{}}
    files=state.setdefault('files',{})
    terminal={'extracted','needs_visual_review','needs_conversion'}
    pending=[e for e in entries if files.get(e['sha'],{}).get('extraction_status') not in terminal
             and files.get(e['sha'],{}).get('attempts',0)<MAX_ATTEMPTS]
    if pending:
        entry=pending[0];sha=entry['sha'];previous=files.get(sha,{})
        attempts=previous.get('attempts',0)+1
        try: status=extract(entry,download_blob(sha))
        except Exception as exc: status={'extraction_status':'failed','error':str(exc)[:500]}
        status.update({'source_name':entry['name'],'category':entry['category'],
                       'attempts':attempts,'last_attempt_utc':datetime.now(timezone.utc).isoformat(),
                       'visual_review_complete':False,'fact_checked':False,
                       'integrated_into_lesson':False})
        files[sha]=status
    else:
        entry=None;status={'extraction_status':'no_eligible_files'}
    state['schema_version']=2
    STATE.parent.mkdir(parents=True,exist_ok=True)
    STATE.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    counts={s:sum(v.get('extraction_status')==s for v in files.values())
            for s in ('extracted','needs_visual_review','needs_conversion','failed')}
    exhausted=sum(v.get('extraction_status')=='failed' and v.get('attempts',0)>=MAX_ATTEMPTS
                  for v in files.values())
    reviewed=sum(bool(v.get('visual_review_complete')) for v in files.values())
    checked=sum(bool(v.get('fact_checked')) for v in files.values())
    integrated=sum(bool(v.get('integrated_into_lesson')) for v in files.values())
    REPORT.write_text('# The Market Mind — 178份原件自动处理进度\n\n'
       +f'- 本轮：{entry["name"] if entry else "无可处理文件"}\n'
       +f'- 本轮状态：{status["extraction_status"]}\n'
       +f'- 已提取文字：{counts["extracted"]}/178\n'
       +f'- 需视觉复核：{counts["needs_visual_review"]}\n'
       +f'- 需旧格式转换：{counts["needs_conversion"]}\n'
       +f'- 失败待重试：{counts["failed"]-exhausted}；重试耗尽：{exhausted}\n'
       +f'- 完成图表视觉核验：{reviewed}；完成事实核验：{checked}；完成课程融合：{integrated}\n\n'
       +'**提取文字不代表理解或核验。** 原件和提取全文不提交到公开仓库。\n',encoding='utf-8')
    print(json.dumps({'file':entry,'result':status,'counts':counts},ensure_ascii=False))
    if status['extraction_status']=='failed':sys.exit(1)

if __name__=='__main__': main()
