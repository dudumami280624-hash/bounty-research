#!/usr/bin/env python3
"""Resume bounded PDF page-level visual feature coverage, never semantic verification."""
import json, os, tempfile, time, signal
from datetime import datetime, timezone, timedelta
from pathlib import Path
from run_extraction_batch import ROOT, INDEX, STATE, inventory, download_blob
from free_visual import inspect_pdf

def next_retry_page(failed_pages, cooldowns, now):
    """Choose first eligible failed 1-based page; never strand others behind one failure."""
    for candidate in failed_pages:
        try:
            ready=datetime.fromisoformat(cooldowns[str(candidate)])<=now
        except (KeyError, ValueError, TypeError):
            ready=True
        if ready:
            return candidate
    return None

def validate_visual_window(observations, start):
    """Reject invalid scan output; never turn empty results into completed coverage."""
    # Empty/invalid windows are errors, not proof of full coverage.
    # A zero-page response previously marked coverage_complete=True (0 >= 0).
    if not observations:
        raise RuntimeError('Visual scanner returned zero observations; retain checkpoint for retry')
    total=observations[0]['document_total_pages']
    if not isinstance(total,int) or total<=0:
        raise RuntimeError(f'Invalid PDF page count: {total!r}')
    if start>=total:
        raise RuntimeError(f'Visual checkpoint {start} beyond PDF page count {total}')
    if start+len(observations)>total:
        raise RuntimeError('Visual scanner returned pages beyond document length')
    expected=list(range(start+1,start+len(observations)+1))
    actual=[x.get('page') for x in observations]
    if actual!=expected:
        raise RuntimeError(f'Noncontiguous visual page observations: expected {expected}, got {actual}')
    return total

def retain_page_evidence(audit, observations):
    """Persist only page hashes and unverified feature counts, never page contents."""
    page_evidence=audit.setdefault('page_evidence',{})
    for observation in observations:
        page_evidence[str(observation['page'])]={
            'render_sha256':observation['render_sha256'],
            'ocr_success':bool(observation.get('ocr_success',False)),
            'ocr_actually_performed':bool(observation.get('ocr_performed',False)),
            'ocr_actual_success':bool(observation.get('ocr_performed',False) and observation.get('ocr_success',False)),
            'embedded_text_available':observation.get('text_origin')=='embedded_pdf_text',
            'text_origin':observation.get('text_origin','legacy_unknown'),
            'ocr_performed':observation.get('ocr_performed'),
            'ocr_text_characters':int(observation.get('ocr_text_characters',0)),
            'chart_candidate_unverified':bool(observation.get('chart_candidate',False)),
        }

def update_page_retry_cooldowns(audit, observations, failed, now):
    """Per-page retry schedule; successful OCR clears its own cooldown."""
    cooldowns=audit.setdefault('ocr_page_retry_after_utc',{})
    retry_at=(now+timedelta(hours=6)).isoformat()
    for observation in observations:
        key=str(observation['page'])
        if observation['page'] in failed:
            cooldowns[key]=retry_at
        else:
            cooldowns.pop(key,None)
    audit.pop('ocr_retry_after_utc',None)

def adaptive_window_pages(configured, attempts):
    """Shrink OCR-heavy windows after deadline failures without losing the page checkpoint."""
    return max(1, configured // (2 ** min(max(0, attempts), 5)))

def visual_priority(entry, files):
    """Fair rotation inside the first-26 group, then the remaining sources.

    A fixed -next_page ordering repeatedly favored the longest started PDFs.
    Sort by last successful window (oldest first), retaining started-before-new
    as a tie-breaker. This does not certify OCR or chart semantics.
    """
    audit=files[entry['sha']].get('visual_page_audit',{})
    next_page=max(0,int(audit.get('next_page',0)))
    return (0 if entry['category'].startswith('01-') else 1,
            bool(audit.get('coverage_complete',False)),
            audit.get('last_advanced_utc',''),
            0 if next_page>0 else 1,
            entry['name'])

def main():
    state=json.loads(STATE.read_text(encoding='utf-8'))
    files=state['files']
    entries=[e for e in inventory(INDEX.read_text(encoding='utf-8'))
             if e['name'].lower().endswith('.pdf') and
             files.get(e['sha'],{}).get('extraction_status') in ('extracted','partial_ocr_failure','needs_visual_review')]
    # Prioritize unfinished first-pass coverage over retries of already visited pages.
    # Otherwise the first two OCR-heavy books can consume every hourly window.
    entries.sort(key=lambda e: visual_priority(e,files))
    budget=int(os.environ.get('TMM_VISUAL_AUDIT_BUDGET_SECONDS','145'))
    started=time.monotonic()
    completed=0
    # Do not impose a two-file ceiling when short PDF windows leave time unused.
    max_windows=max(1,min(12,int(os.environ.get('TMM_VISUAL_WINDOWS_PER_RUN','6'))))
    for e in entries:
        if time.monotonic()-started>=budget or completed>=max_windows: break
        record=files[e['sha']]
        audit=record.setdefault('visual_page_audit',{'next_page':0,'total_pages':None,'attempts':0,
            'coverage_complete':False,'semantic_verified':False})
        # Do not permanently strand a PDF after three transient network/OCR failures.
        # Retry after a cooldown; the per-window alarm still bounds runtime.
        if 'ocr_failed_page_numbers' not in audit and audit.get('ocr_failed_pages_total',0):
            audit['ocr_failures_without_page_locations']=True
        # Historical OCR failure counts lack page locators; re-audit all pages once.
        # Preserve the unknown-failure flag until the full pass finishes.
        if (audit.get('coverage_complete')
                and audit.get('ocr_failures_without_page_locations')
                and not audit.get('legacy_reaudit_started')):
            audit['next_page']=0
            audit['coverage_complete']=False
            audit['legacy_reaudit_started']=True
            audit['ocr_failed_page_numbers']=[]
        failed_pages=list(audit.get('ocr_failed_page_numbers',[]))
        retry_page=(next_retry_page(failed_pages,audit.get('ocr_page_retry_after_utc',{}),datetime.now(timezone.utc))
                    if audit.get('coverage_complete') else None)
        if audit.get('coverage_complete') and retry_page is None: continue
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
        start=retry_page-1 if retry_page is not None else int(audit.get('next_page',0))
        print(f'VISUAL BEGIN {e["name"]!r} start_page={start}',flush=True)
        def timeout(_sig,_frame): raise TimeoutError('Visual page window exceeded 65 seconds')
        previous=signal.signal(signal.SIGALRM,timeout)
        try:
            signal.alarm(65)
            with tempfile.TemporaryDirectory() as td:
                path=Path(td)/'source.pdf'
                path.write_bytes(download_blob(e['sha']))
                # Retry only the failed page, not the already scanned PDF window.
                old_limit=os.environ.get('TMM_VISUAL_MAX_PAGES')
                configured=max(1,int(old_limit or '12'))
                # A 12-page OCR window can exceed the 65-second hard deadline.
                # Halve it on each failure, eventually retrying one page at a time.
                os.environ['TMM_VISUAL_MAX_PAGES']=str(1 if retry_page is not None else adaptive_window_pages(configured,audit.get('attempts',0)))
                try:
                    observations=inspect_pdf(path,Path(td)/'pages',start_page=start)
                finally:
                    if old_limit is None: os.environ.pop('TMM_VISUAL_MAX_PAGES',None)
                    else: os.environ['TMM_VISUAL_MAX_PAGES']=old_limit
            total=validate_visual_window(observations,start)
            audit['total_pages']=total
            if retry_page is None: audit['next_page']=start+len(observations)
            # Coverage means every page was visited; OCR failures remain explicitly unresolved.
            audit['coverage_complete']=audit['next_page']>=total
            failed=set(audit.get('ocr_failed_page_numbers',[]))
            for observation in observations:
                page_number=observation['page']
                if observation.get('ocr_success',False): failed.discard(page_number)
                else: failed.add(page_number)
            audit['ocr_failed_page_numbers']=sorted(failed)
            retain_page_evidence(audit, observations)
            # Schedule *every* failed page independently, including first-pass
            # failures. Previously first-pass failures had no cooldown and could
            # immediately consume all six hourly windows on the same pages.
            update_page_retry_cooldowns(audit, observations, failed, datetime.now(timezone.utc))
            audit['ocr_failed_pages_total']=len(failed)
            # Old audits recorded counts without page numbers; never silently certify them.
            if audit.get('legacy_reaudit_started') and audit['coverage_complete']:
                audit['ocr_failures_without_page_locations']=False
                audit.pop('legacy_reaudit_started',None)
            legacy_unknown=bool(audit.get('ocr_failures_without_page_locations',False))
            audit['ocr_complete']=audit['coverage_complete'] and not failed and not legacy_unknown
            audit['attempts']=0
            audit['last_advanced_utc']=datetime.now(timezone.utc).isoformat()
            audit.pop('last_error',None)
            audit.pop('retry_after_utc',None)
            # No original image, OCR text, or copyrighted content persisted.
            audit['last_window']={'first_page':start+1,'last_page':start+len(observations),
                'candidate_pages':sum(bool(x['chart_candidate']) for x in observations),
                'ocr_failed_pages':sum(not x.get('ocr_success',False) for x in observations),
                'render_sha256':[x['render_sha256'] for x in observations]}
            print(f'VISUAL END next={audit["next_page"]}/{total} failed_pages={audit["ocr_failed_page_numbers"]}',flush=True)
        except Exception as exc:
            audit['attempts']=audit.get('attempts',0)+1
            audit['last_error']=str(exc)[:250]
            if audit['attempts']>=3:
                audit['retry_after_utc']=(datetime.now(timezone.utc)+timedelta(hours=6)).isoformat()
            print(f'VISUAL ERROR {e["name"]!r}: {exc}',flush=True)
        finally:
            signal.alarm(0)
            signal.signal(signal.SIGALRM,previous)
            checkpoint=STATE.with_suffix('.visual.tmp')
            checkpoint.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            checkpoint.replace(STATE)
        completed+=1
    pdf_audits=[v['visual_page_audit'] for v in files.values() if 'visual_page_audit' in v]
    covered=sum(a.get('coverage_complete',False) for a in pdf_audits)
    blocked=sum(a.get('attempts',0)>=3 for a in pdf_audits)
    ocr_incomplete=sum(a.get('coverage_complete') and not a.get('ocr_complete',False) for a in pdf_audits)
    actual_ocr_success=sum(sum(bool(p.get('ocr_actual_success')) for p in a.get('page_evidence',{}).values()) for a in pdf_audits)
    embedded_text_pages=sum(sum(bool(p.get('embedded_text_available')) for p in a.get('page_evidence',{}).values()) for a in pdf_audits)
    (ROOT/'integration/visual-page-coverage-progress.md').write_text(
        '# PDF page-level visual coverage (not semantic verification)\n\n'
        +f'- PDF files with tracked visual audit: {len(pdf_audits)}\n'
        +f'- Page coverage complete: {covered}\n'
        +f'- Windows attempted this run: {completed}\n'
        +f'- Repeated failures cooling down for automatic retry: {blocked}\n'
        +f'- Page coverage finished but OCR incomplete: {ocr_incomplete}\n'
        +f'- Actual OCR success pages (new evidence only): {actual_ocr_success}\n'
        +f'- Embedded-text pages (new evidence only, not OCR): {embedded_text_pages}\n'
        +'- Chart semantics independently verified: 0 (not performed by this scanner)\n'
        +'- Source page hashes and positions only; no copyrighted pages or OCR excerpts.\n',encoding='utf-8')
    print(json.dumps({'windows_attempted':completed,'page_coverage_only':True}))

if __name__=='__main__': main()
