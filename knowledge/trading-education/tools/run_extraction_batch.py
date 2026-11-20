#!/usr/bin/env python3
"""Process one indexed source per invocation, safely persisting metadata only.
Requires: GITHUB_TOKEN, GITHUB_REPOSITORY; Python 3.11, pymupdf.
Downloads binary from GitHub Git Blobs API by the exact SHA in the index.
Extracted copyrighted text remains in the runner and optional Actions artifact,
never in public Git commits. Full visual/factual review is a separate stage.
"""
import base64, hashlib, json, os, re, subprocess, sys, tempfile, urllib.request
from pathlib import Path
from extract_source import ooxml, pdf

ROOT=Path(__file__).resolve().parents[1]
INDEX=ROOT/'integration/source-inventory-178-2026-11-20.md'
STATE=ROOT/'integration/extraction-state.json'
REPORT=ROOT/'integration/latest-extraction-report.md'
REPO=os.environ.get('GITHUB_REPOSITORY','dudumami280624-hash/bounty-research')
TOKEN=os.environ.get('GITHUB_TOKEN','')

def main():
    if not TOKEN: raise RuntimeError('GITHUB_TOKEN missing')
    raw=INDEX.read_text(encoding='utf-8')
    section=raw.split('## 01-蜡烛图与价格行为（26份）',1)[1].split('\n## ',1)[0]
    items=re.findall(r'^- `([^`]+)` .*?Git blob SHA-1 `([0-9a-f]{40})`',section,re.M)
    if len(items)!=26: raise RuntimeError(f'Expected 26 indexed files, got {len(items)}')
    state=json.loads(STATE.read_text(encoding='utf-8')) if STATE.exists() else {'files':{}}
    selected=next(((name,sha) for name,sha in items if state['files'].get(sha,{}).get('extraction_status') not in ('extracted','unsupported')),None)
    if not selected:
        print('All indexed 26 sources have a terminal extraction status');return
    name,sha=selected
    url=f'https://api.github.com/repos/{REPO}/git/blobs/{sha}'
    req=urllib.request.Request(url,headers={'Authorization':f'Bearer {TOKEN}','Accept':'application/vnd.github+json','X-GitHub-Api-Version':'2022-11-28'})
    try:
        with urllib.request.urlopen(req,timeout=180) as response: data=json.load(response)
        if data.get('encoding')!='base64': raise ValueError('Unexpected Git blob encoding')
        blob=base64.b64decode(data['content'])
        gitsha=hashlib.sha1(b'blob '+str(len(blob)).encode()+b'\0'+blob).hexdigest()
        if gitsha!=sha: raise ValueError('Git blob SHA mismatch')
        ext=Path(name).suffix.lower()
        if ext not in ('.docx','.pptx','.pdf'):
            status={'extraction_status':'unsupported','reason':f'Unsupported format {ext}','source_name':name}
            blocks=[];images=[];details={}
        else:
            with tempfile.TemporaryDirectory() as tmp:
                path=Path(tmp)/('source'+ext);path.write_bytes(blob)
                blocks,images,details=(pdf(path) if ext=='.pdf' else ooxml(path,ext[1:]))
                # Text is kept only in a temporary artifact for manual review; no public commit.
                art=Path(os.environ.get('RUNNER_TEMP',tmp))/'tmm-private-extraction'
                art.mkdir(parents=True,exist_ok=True)
                (art/'extracted_text.md').write_text('\n\n'.join(
                    f"### {b['location']}\n{b['text']}" for b in blocks),encoding='utf-8')
                (art/'image_inventory.json').write_text(json.dumps(images,ensure_ascii=False,indent=2),encoding='utf-8')
                (art/'source_manifest.json').write_text(json.dumps({'name':name,'sha':sha,'details':details},ensure_ascii=False,indent=2),encoding='utf-8')
            status={'extraction_status':'extracted','source_name':name,'source_sha256':hashlib.sha256(blob).hexdigest(),
                    'text_blocks':len(blocks),'images_found':len(images),'details':details,
                    'visual_review_complete':False,'fact_checked':False,'integrated_into_lesson':False}
    except Exception as exc:
        status={'extraction_status':'failed','source_name':name,'error':str(exc)[:350]}
    state['files'][sha]=status
    STATE.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    counts={s:sum(v.get('extraction_status')==s for v in state['files'].values()) for s in ('extracted','failed','unsupported')}
    REPORT.write_text('# The Market Mind — 自动原件提取进度\n\n'
                      f'- 本轮文件：`{name}`\n- 状态：`{status["extraction_status"]}`\n'
                      f'- 已提取：{counts["extracted"]}/26；失败：{counts["failed"]}；不支持：{counts["unsupported"]}\n'
                      '- **提取≠逐页视觉核验≠事实核验≠课程融合。**\n'
                      '- 原文及图表不提交到公开仓库；只有元数据入库。\n',encoding='utf-8')
    print(json.dumps(status,ensure_ascii=False))
    if status['extraction_status']=='failed':sys.exit(1)

if __name__=='__main__':main()
