#!/usr/bin/env python3
"""Resume bounded PDF page-level visual feature coverage, never semantic verification."""
import json, os, tempfile, time, signal
from datetime import datetime, timezone, timedelta
from pathlib import Path
from run_extraction_batch import ROOT, INDEX, STATE, inventory, download_blob
from free_visual import inspect_pdf

def main():
    state=json.loads(STATE.read_text(encoding='utf-8'))
    files=state['files']
    entries=[e for e in inventory(INDEX.read_text(encoding='utf-8'))
             if e['name'].lower().endswith('.pdf') and
             files.get(e['sha'],{}).get('extraction_status') in ('extracted','partial_ocr_failure','needs_visual_review')]
    budget=int(os.environ.get('TMM_VISUAL_AUDIT_BUDGET_SECONDS','145'))
    started=time.monotonic()
    completed=0
    for e in entries:
        if time.monotonic()-started>=budget or completed>=2: break
        record=files[e['sha']]
        audit=record.setdefault('visual_page_audit',{'next_page':0,'total_pages':None,'attempts':0,
            'coverage_complete':False,'semantic_verified':False})
        # Do not permanently strand a PDF after three transient network/OCR failures.
        # Retry after a cooldown; the per-window alarm still bounds runtime.
        if audit.get('coverage_complete'): continue
        if audit.get('attempts',0)>=3:
            retry_after=audit.get('retry_after_utc')
            if retry_after:
                try:
                    if datetime.fromisoformat(retry_after)<datetime.now(timezone.utc):
                        audit['attempts']=0
                    else: continue
                except ValueError:
                    audit['attempts']=0
            else:
                audit['attempts']=0
        start=int(audit.get('next_page',0))
        print(f'VISUAL BEGIN {e["name"]!r} start_page={start}',flush=True)
        def timeout(_sig,_frame): raise TimeoutError('Visual page window exceeded 65 seconds')
        previous=signal.signal(signal.SIGALRM,timeout)
        try:
            signal.alarm(65)
            with tempfile.TemporaryDirectory() as td:
                path=Path(td)/'source.pdf'
                path.write_bytes(download_blob(e['sha']))
                observations=inspect_pdf(path,Path(td)/'pages',start_page=start)
            total=observations[0]['document_total_pages'] if observations else 0
            audit['total_pages']=total
            audit['next_page']=start+len(observations)
            # Coverage means every page was visited; OCR failures remain explicitly unresolved.
            audit['coverage_complete']=audit['next_page']>=total
            audit['ocr_failed_pages_total']=audit.get('ocr_failed_pages_total',0)+sum(
                not x.get('ocr_success',False) for x in observations)
            audit['ocr_complete']=audit['coverage_complete'] and audit['ocr_failed_pages_total']==0
            audit['attempts']=0
            audit.pop('last_error',None)
            audit.pop('retry_after_utc',None)
            # No original image, OCR text, or copyrighted content persisted.
            audit['last_window']={'first_page':start+1,'last_page':audit['next_page'],
                'candidate_pages':sum(bool(x['chart_candidate']) for x in observations),
                'ocr_failed_pages':sum(not x.get('ocr_success',False) for x in observations),
                'render_sha256':[x['render_sha256'] for x in observations]}
            print(f'VISUAL END next={audit["next_page"]}/{total}',flush=True)
        except Exception as exc:
            audit['attempts']=audit.get('attempts',0)+1
            audit['last_error']=str(exc)[:250]
            if audit['attempts']>=3:
                audit['retry_after_utc']=(datetime.now(timezone.utc)+timedelta(hours=6)).isoformat()
            print(f'VISUAL ERROR {e["name"]!r}: {exc}',flush=True)
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM,previous)
            STATE.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
        completed+=1
    pdf_audits=[v['visual_page_audit'] for v in files.values() if 'visual_page_audit' in v]
    covered=sum(a.get('coverage_complete',False) for a in pdf_audits)
    blocked=sum(a.get('attempts',0)>=3 for a in pdf_audits)
    ocr_incomplete=sum(a.get('coverage_complete') and not a.get('ocr_complete',False) for a in pdf_audits)
    (ROOT/'integration/visual-page-coverage-progress.md').write_text(
        '# PDF page-level visual coverage (not semantic verification)\n\n'
        +f'- PDF files with tracked visual audit: {len(pdf_audits)}\n'
        +f'- Page coverage complete: {covered}\n'
        +f'- Windows attempted this run: {completed}\n'
        +f'- Repeated failures cooling down for automatic retry: {blocked}\n'
        +f'- Page coverage finished but OCR incomplete: {ocr_incomplete}\n'
        +'- Chart semantics independently verified: 0 (not performed by this scanner)\n'
        +'- Source page hashes and positions only; no copyrighted pages or OCR excerpts.\n',encoding='utf-8')
    print(json.dumps({'windows_attempted':completed,'page_coverage_only':True}))

if __name__=='__main__': main()
