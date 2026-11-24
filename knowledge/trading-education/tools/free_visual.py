#!/usr/bin/env python3
"""Free offline visual inspection using PyMuPDF and Tesseract.
Produces page-image evidence and OCR; does NOT claim semantic chart understanding.
"""
import hashlib, json, shutil, subprocess, tempfile, os, re, time
from pathlib import Path

def inspect_pdf(pdf_path, output, start_page=0):
    import fitz
    doc=fitz.open(pdf_path);out=Path(output);out.mkdir(parents=True,exist_ok=True)
    langs=subprocess.run(['tesseract','--list-langs'],capture_output=True,text=True).stdout if shutil.which('tesseract') else ''
    ocr_lang='eng+chi_sim' if 'chi_sim' in langs else 'eng'
    result=[]
    ocr_timeout=max(1,min(120,int(os.environ.get('TMM_OCR_PAGE_TIMEOUT_SECONDS','12'))))
    # A bounded visual sample prevents huge PDFs from monopolizing the hourly batch.
    # Record incomplete coverage explicitly; this is not a full chart audit.
    max_pages=max(1,int(os.environ.get('TMM_VISUAL_MAX_PAGES','12')))
    total_pages=len(doc)
    start_page=max(0,int(start_page))
    window_started=time.monotonic()
    # Allow many fast selectable-text pages, but stop before the next expensive
    # OCR call could exhaust the outer 65-second checkpoint alarm.
    window_budget=max(ocr_timeout+4,min(58,int(os.environ.get('TMM_VISUAL_WINDOW_BUDGET_SECONDS','52'))))
    for index in range(start_page,min(total_pages,start_page+max_pages)):
        if result and time.monotonic()-window_started+ocr_timeout+3>=window_budget:
            break
        page=doc[index]
        pix=page.get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False)
        png=pix.tobytes('png')
        record={'page':index+1,'render_sha256':hashlib.sha256(png).hexdigest(),
                'image_objects':len(page.get_images(full=True)),
                'vector_drawings':len(page.get_drawings()),
                'status':'visual_features_extracted_unverified',
                'document_total_pages':total_pages,
                'visual_sample_limit':max_pages,
                'visual_coverage_complete':False,
                'visual_window_start':start_page}
        embedded_text=page.get_text('text').strip()
        record['embedded_text_characters']=len(embedded_text)
        # A page number, running header or watermark is not evidence that a
        # scanned chart/table has been transcribed. OCR sparse-text pages too.
        meaningful_chars=len(re.sub(r'\s+', '', embedded_text))
        sparse_embedded=bool(embedded_text) and meaningful_chars<80
        # A genuinely empty PDF page needs no text OCR. Do not confuse it with
        # a raster/vector chart whose OCR returned an empty string.
        record['visually_blank_no_ocr_needed']=bool(not meaningful_chars and
            record['image_objects']==0 and record['vector_drawings']==0)
        record['embedded_text_sparse']=sparse_embedded
        # Embedded text may be a caption over an image-only chart. If the page
        # contains raster images, OCR the rendered page too rather than treating
        # its caption as full chart text coverage. Vector drawings alone are
        # common for text glyphs and should not force OCR on every text PDF.
        raster_chart_with_text=bool(embedded_text and record['image_objects']>0)
        record['raster_with_embedded_text_ocr_needed']=raster_chart_with_text
        if record['visually_blank_no_ocr_needed']:
            record['ocr_success']=False
            record['ocr_performed']=False
            record['text_origin']='visually_blank_page'
            record['ocr_skipped_reason']='no_text_images_or_vector_drawings'
            record['ocr_text_characters']=0
        elif embedded_text and not sparse_embedded and not raster_chart_with_text:
            record['ocr_success']=True  # Legacy field: text available, not necessarily OCR performed
            record['text_origin']='embedded_pdf_text'
            record['ocr_performed']=False
            record['ocr_skipped_reason']='embedded_text_available'
            record['ocr_text_characters']=len(embedded_text)
            record['text_sha256']=hashlib.sha256(embedded_text.encode('utf-8')).hexdigest()
        elif shutil.which('tesseract'):
            record['text_origin']=('embedded_raster_plus_ocr_unverified' if raster_chart_with_text
                else 'embedded_sparse_plus_ocr_unverified' if sparse_embedded else 'ocr_unverified')
            record['ocr_performed']=True
            with tempfile.TemporaryDirectory() as td:
                image=Path(td)/'page.png';image.write_bytes(png)
                ocr_env=dict(os.environ)
                ocr_env.setdefault('OMP_THREAD_LIMIT','1')
                ocr_started=time.monotonic()
                # Reserve time for a different segmentation strategy even when
                # the first invocation times out. Both attempts share one deadline.
                # Reserve part of the page budget for the independent engine when enabled.
                tesseract_budget=ocr_timeout
                if os.environ.get('TMM_RAPIDOCR_FALLBACK') == '1' and ocr_timeout>=8:
                    tesseract_budget=ocr_timeout*0.6
                first_budget=tesseract_budget if tesseract_budget<3 else tesseract_budget*0.65
                proc=None
                try:
                    proc=subprocess.run(['tesseract',str(image),'stdout','-l',ocr_lang],
                        capture_output=True,text=True,timeout=first_budget,env=ocr_env)
                except subprocess.TimeoutExpired:
                    record['ocr_default_mode_timed_out']=True
                    record['ocr_success']=False
                    record['ocr_error']='Default OCR timed out'
                if proc is None or proc.returncode!=0 or not proc.stdout.strip():
                    remaining=tesseract_budget-(time.monotonic()-ocr_started)
                    if remaining>=1:
                        record['ocr_sparse_mode_attempted']=True
                        try:
                            alternate=subprocess.run(['tesseract',str(image),'stdout','-l',ocr_lang,'--psm','11'],
                                capture_output=True,text=True,timeout=remaining,env=ocr_env)
                            if alternate.returncode==0 and alternate.stdout.strip():
                                proc=alternate
                                record['ocr_sparse_mode_recovered']=True
                            elif proc is None:
                                proc=alternate
                        except subprocess.TimeoutExpired:
                            record['ocr_sparse_mode_timed_out']=True
                if proc is None:
                    record['ocr_text_characters']=0
                    record['ocr_success']=False
                    record['ocr_error']='OCR timed out; page requires retry'
                if proc is not None:
                    record['ocr_text_characters']=len(proc.stdout.strip()) if proc.returncode==0 else 0
                    record['ocr_success']=proc.returncode==0 and bool(proc.stdout.strip())
                    if record['ocr_success']:
                        record['text_sha256']=hashlib.sha256(proc.stdout.strip().encode('utf-8')).hexdigest()
                    record['ocr_error']=(proc.stderr[-200:] if proc.returncode else ('OCR returned no text; page requires review' if not proc.stdout.strip() else ''))
        else:
            record['ocr_success']=False
            record['text_origin']=('embedded_raster_ocr_unavailable' if raster_chart_with_text
                else 'embedded_sparse_ocr_unavailable' if sparse_embedded else 'none')
            record['ocr_performed']=False
            record['ocr_error']='Tesseract unavailable'
        # Independent CPU OCR fallback; bounded subprocess, no source text persisted.
        if (not record.get('ocr_success') and not record.get('visually_blank_no_ocr_needed')
                and os.environ.get('TMM_RAPIDOCR_FALLBACK') == '1'):
            remaining=window_budget-(time.monotonic()-window_started)-3
            if remaining<3:
                record['rapidocr_error']='insufficient_window_budget'
            if remaining>=3:
                record['rapidocr_attempted']=True
                try:
                    with tempfile.TemporaryDirectory() as td:
                        image=Path(td)/'page.png';image.write_bytes(png)
                        script="import sys,json; from rapidocr_onnxruntime import RapidOCR; rows,_=RapidOCR()(sys.argv[1]); print(json.dumps([r[1] for r in (rows or [])]))"
                        p=subprocess.run([__import__('sys').executable,'-c',script,str(image)],
                            capture_output=True,text=True,timeout=min(20,remaining))
                        if p.returncode==0:
                            value=' '.join(json.loads(p.stdout.splitlines()[-1])).strip()
                            if value:
                                record.update(ocr_success=True,ocr_performed=True,
                                    text_origin='rapidocr_unverified',ocr_engine='rapidocr_onnxruntime',
                                    ocr_text_characters=len(value),
                                    text_sha256=hashlib.sha256(value.encode('utf-8')).hexdigest(),
                                    ocr_error='')
                            else:
                                record['rapidocr_error']='no_text_returned'
                        else:
                            record['rapidocr_error']='nonzero_exit_'+str(p.returncode)
                except (subprocess.TimeoutExpired, ValueError, IndexError, OSError) as exc:
                    record['rapidocr_error']=type(exc).__name__
        record['chart_candidate']=bool(record['vector_drawings']>=12 or record['image_objects']>0)
        record['chart_semantics_verified']=False
        (out/f'page-{index+1:04}.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
        result.append(record)
    # The elapsed-time budget may end a window before max_pages is reached.
    # Completion must reflect the last page actually written, not the requested window.
    if result:
        result[-1]['visual_coverage_complete'] = result[-1]['page'] >= total_pages
        last_path = out / f"page-{result[-1]['page']:04}.json"
        last_path.write_text(json.dumps(result[-1], ensure_ascii=False, indent=2) + '\n')
    doc.close()
    return result

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('pdf');parser.add_argument('--out',required=True)
    args=parser.parse_args();print(json.dumps({'pages':len(inspect_pdf(args.pdf,args.out))}))
