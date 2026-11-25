#!/usr/bin/env python3
"""Resume bounded PDF page-level visual feature coverage, never semantic verification."""
import json, os, tempfile, time, signal
from datetime import datetime, timezone, timedelta
from pathlib import Path
from run_extraction_batch import ROOT, INDEX, STATE, inventory, download_blob
from free_visual import inspect_pdf

def bounded_failed_pages(failed_pages, total_pages):
    """Drop malformed or impossible persisted OCR page locators after PDF inspection."""
    valid=set()
    for candidate in failed_pages:
        if isinstance(candidate, bool):
            continue
        try:
            page=int(candidate)
            if str(candidate).strip()==str(page) and 1<=page<=total_pages:
                valid.add(page)
        except (TypeError, ValueError):
            continue
    return valid

def next_retry_page(failed_pages, cooldowns, now, total_pages=None):
    """Choose first eligible failed 1-based page; never strand others behind one failure."""
    for candidate in failed_pages:
        # Older checkpoints may encode page numbers as strings. Normalize before
        # arithmetic; otherwise retry_page - 1 raises TypeError every run.
        # Reject invalid 0/negative/noninteger locators without blocking later pages.
        try:
            page=int(candidate)
            if (page<1 or isinstance(candidate,bool) or str(candidate).strip()!=str(page)
                    or (isinstance(total_pages,int) and total_pages>0 and page>total_pages)):
                continue
        except (ValueError,TypeError):
            continue
        try:
            deadline=datetime.fromisoformat(cooldowns[str(page)])
            # Historical checkpoints may contain naive timestamps; normalize to UTC.
            if deadline.tzinfo is None:
                deadline=deadline.replace(tzinfo=timezone.utc)
            ready=deadline<=now
        except (KeyError, ValueError, TypeError):
            ready=True
        if ready:
            return page
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
    # A corrupt/partial renderer response must never advance persistent checkpoints.
    # Source hashes are evidence locators; missing or inconsistent metadata cannot
    # be treated as successful visitation of an original textbook page.
    for observation in observations:
        if observation.get('document_total_pages') != total:
            raise RuntimeError('Inconsistent PDF total page counts within visual window')
        digest=observation.get('render_sha256')
        if not isinstance(digest,str) or len(digest)!=64 or any(c not in '0123456789abcdef' for c in digest):
            raise RuntimeError(f"Missing or invalid rendered-page SHA-256 for page {observation.get('page')}")
    return total

def retain_page_evidence(audit, observations):
    """Persist only page hashes and unverified feature counts, never page contents."""
    page_evidence=audit.setdefault('page_evidence',{})
    for observation in observations:
        previous=page_evidence.get(str(observation['page']),{})
        # A transient OCR timeout must not erase an earlier successful result
        # for the same rendered page. Different render hashes are not comparable.
        if (previous.get('ocr_actual_success') and not observation.get('ocr_success')
                and previous.get('render_sha256')==observation.get('render_sha256')):
            continue
        page_evidence[str(observation['page'])]={
            'render_sha256':observation['render_sha256'],
            'ocr_success':bool(observation.get('ocr_success',False)),
            'ocr_actually_performed':bool(observation.get('ocr_performed',False)),
            'ocr_actual_success':bool(observation.get('ocr_performed',False) and observation.get('ocr_success',False)),
            'embedded_text_available':observation.get('text_origin')=='embedded_pdf_text',
            'raster_with_embedded_text_ocr_needed':bool(observation.get('raster_with_embedded_text_ocr_needed',False)),
            'visually_blank_no_ocr_needed':bool(observation.get('visually_blank_no_ocr_needed',False)),
            'text_origin':observation.get('text_origin','legacy_unknown'),
            'ocr_engine':observation.get('ocr_engine'),
            'rapidocr_attempted':bool(observation.get('rapidocr_attempted')),
            'rapidocr_error':observation.get('rapidocr_error'),
            'ocr_performed':observation.get('ocr_performed'),
            'ocr_text_characters':int(observation.get('ocr_text_characters',0)),
            'text_sha256':observation.get('text_sha256'),
            'chart_candidate_unverified':bool(observation.get('chart_candidate',False)),
        }

def page_ocr_resolved(observation, previous):
    """True only when a page no longer requires OCR, or has genuine OCR evidence.

    Legacy ocr_success=True may mean selectable PDF text, not Tesseract.
    """
    actual_success=bool(observation.get('ocr_performed') and observation.get('ocr_success'))
    preserved=bool(previous.get('ocr_actual_success')
                   and previous.get('render_sha256')==observation.get('render_sha256'))
    text_only=bool(observation.get('text_origin')=='embedded_pdf_text'
                   and not observation.get('raster_with_embedded_text_ocr_needed')
                   and not observation.get('ocr_performed'))
    # Only truly empty pages (no text, raster or vector marks) can be resolved
    # without OCR. An image-only K-line chart with empty OCR stays in retry.
    blank=bool(observation.get('visually_blank_no_ocr_needed') and
               observation.get('text_origin')=='visually_blank_page' and
               not observation.get('ocr_performed') and
               observation.get('image_objects')==0 and
               observation.get('vector_drawings')==0 and
               observation.get('embedded_text_characters')==0)
    return actual_success or preserved or text_only or blank

def verified_ocr_page_coverage(audit):
    """Require evidence for every numbered page before claiming OCR queue complete.

    A legacy checkpoint may say coverage_complete without retaining complete
    page-level OCR/embedded-text evidence. Never certify those gaps.
    """
    total=audit.get('total_pages')
    evidence=audit.get('page_evidence',{})
    if not isinstance(total,int) or total<=0 or not isinstance(evidence,dict):
        return False
    for number in range(1,total+1):
        item=evidence.get(str(number))
        if not isinstance(item,dict):
            return False
        digest=item.get('render_sha256')
        if not isinstance(digest,str) or len(digest)!=64 or any(c not in '0123456789abcdef' for c in digest):
            return False
        # Selectable text alone cannot clear a raster-chart OCR requirement.
        # Persisted legacy evidence without this distinction must remain unverified.
        embedded_only=(item.get('embedded_text_available')
                       and item.get('text_origin')=='embedded_pdf_text'
                       and item.get('raster_with_embedded_text_ocr_needed') is False)
        blank=(item.get('visually_blank_no_ocr_needed')
               and item.get('text_origin')=='visually_blank_page')
        if not (item.get('ocr_actual_success') or embedded_only or blank):
            return False
    return True

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

def needs_legacy_reaudit(audit):
    """Legacy OCR failure counts without page IDs require a bounded full re-audit.

    An existing empty list is not proof that historical failures were located.
    """
    return bool(audit.get('ocr_failed_pages_total', 0) > 0
                and not audit.get('ocr_failed_page_numbers')
                and not audit.get('legacy_reaudit_started')
                and audit.get('ocr_failures_without_page_locations') is not False)


def visual_priority(entry, files):
    """Fair rotation inside the first-26 group, then the remaining sources.

    A fixed -next_page ordering repeatedly favored the longest started PDFs.
    Sort by last successful window (oldest first), retaining started-before-new
    as a tie-breaker. This does not certify OCR or chart semantics.
    """
    audit=files[entry['sha']].get('visual_page_audit',{})
    next_page=max(0,int(audit.get('next_page',0)))
    # A previous scanner skipped raster-chart OCR on pages with long captions.
    # Revisit completed legacy audits once under the revised scanner, without
    # claiming old coverage as new OCR or discarding old page evidence.
    stale=bool(audit.get('coverage_complete') and audit.get('scanner_revision',0)<2)
    # Completed audits with failed OCR pages must eventually receive retry time.
    # Rotate due retries alongside unfinished books rather than placing every
    # completed book behind the entire unfinished inventory indefinitely.
    due_retry=(bool(audit.get('coverage_complete')) and bool(next_retry_page(
        audit.get('ocr_failed_page_numbers',[]), audit.get('ocr_page_retry_after_utc',{}),
        datetime.now(timezone.utc), audit.get('total_pages'))))
    return (0 if entry['category'].startswith('01-') else 1,
            0 if due_retry else (1 if stale or not audit.get('coverage_complete',False) else 2),
            audit.get('last_advanced_utc',''),
            0 if next_page>0 else 1,
            entry['name'])

def interleave_visual_work(entries, files):
    """Interleave due retries and unfinished audits without crossing source tiers.

    A flood of due OCR pages must not monopolize all windows, and unfinished
    PDFs must not permanently starve retryable pages. Only scheduling changes;
    no page is marked reviewed or complete.
    """
    ordered=[]
    for tier in (0,1):
        group=[e for e in entries if (0 if e['category'].startswith('01-') else 1)==tier]
        group.sort(key=lambda e:visual_priority(e,files))
        # A completed legacy audit may also have a due OCR retry. Treat it as
        # retry work first; otherwise it can flood the unfinished queue and
        # starve genuine first-pass coverage (see test_visual_interleave.py).
        now=datetime.now(timezone.utc)
        def due(e):
            a=files[e['sha']].get('visual_page_audit',{})
            return bool(a.get('coverage_complete') and next_retry_page(
                a.get('ocr_failed_page_numbers',[]),
                a.get('ocr_page_retry_after_utc',{}), now, a.get('total_pages')))
        retries=[e for e in group if due(e)]
        unfinished=[e for e in group if not due(e) and (
            not files[e['sha']].get('visual_page_audit',{}).get('coverage_complete',False)
            or files[e['sha']].get('visual_page_audit',{}).get('scanner_revision',0)<2
            or needs_legacy_reaudit(files[e['sha']].get('visual_page_audit',{})))]
        while unfinished or retries:
            for _ in range(2):
                if unfinished: ordered.append(unfinished.pop(0))
            if retries: ordered.append(retries.pop(0))
        # Completed audits with no due retry remain safe to skip in main.
    return ordered

def mark_scanner_revision_if_covered(audit):
    """Mark completed page visitation, without claiming OCR/semantic completion."""
    if audit.get('coverage_complete'):
        audit['scanner_revision']=2
        audit.pop('scanner_reaudit_in_progress',None)

def refresh_extraction_visual_summary(report, files, entries):
    """Synchronize only visual counters after scanning; preserve historical text flags."""
    import re
    audits=[v['visual_page_audit'] for v in files.values()
            if isinstance(v.get('visual_page_audit'),dict)]
    covered=sum(bool(a.get('coverage_complete')) for a in audits)
    complete=sum(bool(a.get('ocr_complete')) for a in audits)
    successes=sum(sum(bool(p.get('ocr_actual_success')) for p in
                      a.get('page_evidence',{}).values()) for a in audits)
    eligible=[files.get(e['sha'],{}) for e in entries
              if e['name'].lower().endswith('.pdf') and
              files.get(e['sha'],{}).get('extraction_status') in
              ('extracted','partial_ocr_failure','needs_visual_review')]
    unfinished=sum(not r.get('visual_page_audit',{}).get('coverage_complete',False)
                   for r in eligible)
    failures=sum(len(r.get('visual_page_audit',{}).get('ocr_failed_page_numbers') or [])
                 for r in eligible)
    replacements=[
        (r'^- 视觉页面覆盖未完成源：.*$',f'- 视觉页面覆盖未完成源：{unfinished}份；视觉OCR失败页定位记录：{failures}条'),
        (r'^- 真实OCR成功页面证据：.*$',f'- 真实OCR成功页面证据：{successes}页；视觉逐页覆盖完成：{covered}/{len(audits)}份；视觉OCR队列完成：{complete}份（均非语义或全文验收）')]
    for pattern, value in replacements:
        report=re.sub(pattern,lambda _:value,report,flags=re.M)
    return report

def main():
    state=json.loads(STATE.read_text(encoding='utf-8'))
    files=state['files']
    entries=[e for e in inventory(INDEX.read_text(encoding='utf-8'))
             if e['name'].lower().endswith('.pdf') and
             files.get(e['sha'],{}).get('extraction_status') in ('extracted','partial_ocr_failure','needs_visual_review')]
    # Prioritize unfinished first-pass coverage over retries of already visited pages.
    # Otherwise the first two OCR-heavy books can consume every hourly window.
    # Keep first-pass PDF coverage moving even when many completed PDFs have
    # due OCR retries. Reserve approximately two of every three slots for
    # unfinished audits, while still retrying due failures each run.
    entries=interleave_visual_work(entries,files)
    budget=int(os.environ.get('TMM_VISUAL_AUDIT_BUDGET_SECONDS','145'))
    started=time.monotonic()
    completed=0
    # Do not impose a two-file ceiling when short PDF windows leave time unused.
    max_windows=max(1,min(48,int(os.environ.get('TMM_VISUAL_WINDOWS_PER_RUN','24'))))
    for e in entries:
        if time.monotonic()-started>=budget or completed>=max_windows: break
        record=files[e['sha']]
        audit=record.setdefault('visual_page_audit',{'next_page':0,'total_pages':None,'attempts':0,
            'coverage_complete':False,'semantic_verified':False})
        # Revisit legacy completed PDFs after captioned-raster OCR fix. Persist
        # the revision only after a full second pass; retain source page hashes.
        if audit.get('coverage_complete') and audit.get('scanner_revision',0)<2:
            audit['next_page']=0
            audit['coverage_complete']=False
            audit['ocr_complete']=False
            audit['scanner_reaudit_in_progress']=True
        # Do not permanently strand a PDF after three transient network/OCR failures.
        # Retry after a cooldown; the per-window alarm still bounds runtime.
        if audit.get('ocr_failed_pages_total',0) and not audit.get('ocr_failed_page_numbers') and audit.get('ocr_failures_without_page_locations') is not False:
            audit['ocr_failures_without_page_locations']=True
        # Historical OCR failure counts lack page locators; re-audit all pages once.
        # Preserve the unknown-failure flag until the full pass finishes.
        if (audit.get('coverage_complete')
                and needs_legacy_reaudit(audit)):
            audit['next_page']=0
            audit['coverage_complete']=False
            audit['legacy_reaudit_started']=True
            audit['ocr_failed_page_numbers']=[]
        failed_pages=list(audit.get('ocr_failed_page_numbers',[]))
        retry_page=(next_retry_page(failed_pages,audit.get('ocr_page_retry_after_utc',{}),datetime.now(timezone.utc),audit.get('total_pages'))
                    if audit.get('coverage_complete') else None)
        if audit.get('coverage_complete') and retry_page is None: continue
        if audit.get('attempts',0)>=3:
            retry_after=audit.get('retry_after_utc')
            if retry_after:
                try:
                    deadline=datetime.fromisoformat(retry_after)
                    if deadline.tzinfo is None:
                        deadline=deadline.replace(tzinfo=timezone.utc)
                    if deadline<datetime.now(timezone.utc):
                        audit['attempts']=0
                    else: continue
                except (ValueError, TypeError, OverflowError):
                    # Malformed legacy JSON deadlines must not abort the batch.
                    audit['attempts']=0
                    audit.pop('retry_after_utc',None)
            else:
                audit['attempts']=0
        start=retry_page-1 if retry_page is not None else int(audit.get('next_page',0))
        print(f'VISUAL BEGIN {e["name"]!r} start_page={start}',flush=True)
        def timeout(_sig,_frame): raise TimeoutError('Visual page window exceeded 65 seconds')
        previous_handler=signal.signal(signal.SIGALRM,timeout)
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
                # Bound the OCR worst case to fit the 65-second window alarm.
                # Twelve pages * twelve seconds of Tesseract alone can exceed it;
                # repeatedly timing out the entire window loses all page evidence.
                ocr_timeout=max(1,min(120,int(os.environ.get('TMM_OCR_PAGE_TIMEOUT_SECONDS','12'))))
                # free_visual.py now stops a window before another OCR page can
                # exceed its own 52s budget. Do not cap every selectable-text
                # PDF at four pages merely because *some* pages may need OCR.
                # The scanner returns a contiguous partial window for checkpointing.
                window_pages=1 if retry_page is not None else adaptive_window_pages(configured,audit.get('attempts',0))
                os.environ['TMM_VISUAL_MAX_PAGES']=str(window_pages)
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
            failed=bounded_failed_pages(audit.get('ocr_failed_page_numbers',[]), total)
            for observation in observations:
                page_number=observation['page']
                previous=audit.get('page_evidence',{}).get(str(page_number),{})
                # Embedded selectable text is not proof that a previously failed
                # raster OCR was repaired. Only actual OCR, or a text-only page
                # that genuinely does not need OCR, may clear a failed locator.
                if page_ocr_resolved(observation, previous): failed.discard(page_number)
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
            audit['ocr_complete']=(audit['coverage_complete'] and not failed and not legacy_unknown
                                   and verified_ocr_page_coverage(audit))
            # Stamp every fully scanned PDF with the scanner revision, including
            # first-time audits. Otherwise fresh completed audits retain revision 0
            # and get needlessly re-scanned from page 1 on every later run.
            # Failed OCR pages remain queued independently; this is NOT OCR success.
            mark_scanner_revision_if_covered(audit)
            audit['attempts']=0
            audit['last_advanced_utc']=datetime.now(timezone.utc).isoformat()
            audit.pop('last_error',None)
            audit.pop('retry_after_utc',None)
            # No original image, OCR text, or copyrighted content persisted.
            audit['last_window']={'first_page':start+1,'last_page':start+len(observations),
                'candidate_pages':sum(bool(x['chart_candidate']) for x in observations),
                'ocr_failed_pages':sum(x['page'] in failed for x in observations),
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
            signal.signal(signal.SIGALRM,previous_handler)
            checkpoint=STATE.with_suffix('.visual.tmp')
            checkpoint.write_text(json.dumps(state,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
            checkpoint.replace(STATE)
        completed+=1
    pdf_audits=[v['visual_page_audit'] for v in files.values() if 'visual_page_audit' in v]
    covered=sum(a.get('coverage_complete',False) for a in pdf_audits)
    # Scanner revision 2 re-audits reset coverage_complete until the new pass finishes.
    # Report these separately so a falling covered count is not mistaken for lost page evidence.
    reauditing=sum(bool(a.get('scanner_reaudit_in_progress') or a.get('legacy_reaudit_started'))
                   and not a.get('coverage_complete',False) for a in pdf_audits)
    stale_complete=sum(bool(a.get('coverage_complete')) and a.get('scanner_revision',0)<2
                       for a in pdf_audits)
    current_revision_complete=sum(bool(a.get('coverage_complete')) and a.get('scanner_revision',0)>=2
                                  for a in pdf_audits)
    blocked=sum(a.get('attempts',0)>=3 for a in pdf_audits)
    ocr_incomplete=sum(a.get('coverage_complete') and not a.get('ocr_complete',False) for a in pdf_audits)
    rapidocr_recovered=sum(sum(p.get('text_origin')=='rapidocr_unverified' and bool(p.get('ocr_actual_success')) for p in a.get('page_evidence',{}).values()) for a in pdf_audits)
    actual_ocr_success=sum(sum(bool(p.get('ocr_actual_success')) for p in a.get('page_evidence',{}).values()) for a in pdf_audits)
    embedded_text_pages=sum(sum(bool(p.get('embedded_text_available')) for p in a.get('page_evidence',{}).values()) for a in pdf_audits)
    (ROOT/'integration/visual-page-coverage-progress.md').write_text(
        '# PDF page-level visual coverage (not semantic verification)\n\n'
        +f'- PDF files with tracked visual audit: {len(pdf_audits)}\n'
        +f'- Page coverage complete: {covered}\n'
        +f'- Coverage complete on current scanner revision: {current_revision_complete}\n'
        +f'- Legacy coverage complete awaiting re-audit: {stale_complete}\n'
        +f'- Re-audit in progress (not counted complete): {reauditing}\n'
        +'- Note: re-audit resets the completion flag until every page is revisited; earlier page hashes remain recorded.\n'
        +f'- Windows attempted this run: {completed}\n'
        +f'- Repeated failures cooling down for automatic retry: {blocked}\n'
        +f'- Page coverage finished but OCR incomplete: {ocr_incomplete}\n'
        +f'- Actual OCR success pages (new evidence only): {actual_ocr_success}\n'
        +f'- Independent RapidOCR recovered pages: {rapidocr_recovered}\n'
        +f'- Embedded-text pages (new evidence only, not OCR): {embedded_text_pages}\n'
        +'- Chart semantics independently verified: 0 (not performed by this scanner)\n'
        +'- Source page hashes and positions only; no copyrighted pages or OCR excerpts.\n',encoding='utf-8')
    report_path=ROOT/'integration/latest-extraction-report.md'
    if report_path.exists():
        report_path.write_text(refresh_extraction_visual_summary(report_path.read_text(encoding='utf-8'),files,entries),encoding='utf-8')
    print(json.dumps({'windows_attempted':completed,'page_coverage_only':True}))

if __name__=='__main__': main()
