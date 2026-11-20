#!/usr/bin/env python3
"""Free offline visual inspection using PyMuPDF and Tesseract.
Produces page-image evidence and OCR; does NOT claim semantic chart understanding.
"""
import hashlib, json, shutil, subprocess, tempfile, os
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
    for index in range(start_page,min(total_pages,start_page+max_pages)):
        page=doc[index]
        pix=page.get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False)
        png=pix.tobytes('png')
        record={'page':index+1,'render_sha256':hashlib.sha256(png).hexdigest(),
                'image_objects':len(page.get_images(full=True)),
                'vector_drawings':len(page.get_drawings()),
                'status':'visual_features_extracted_unverified',
                'document_total_pages':total_pages,
                'visual_sample_limit':max_pages,
                'visual_coverage_complete':start_page+max_pages>=total_pages,
                'visual_window_start':start_page}
        embedded_text=page.get_text('text').strip()
        record['embedded_text_characters']=len(embedded_text)
        if embedded_text:
            record['ocr_success']=True
            record['ocr_skipped_reason']='embedded_text_available'
            record['ocr_text_characters']=len(embedded_text)
        elif shutil.which('tesseract'):
            with tempfile.TemporaryDirectory() as td:
                image=Path(td)/'page.png';image.write_bytes(png)
                try:
                    proc=subprocess.run(['tesseract',str(image),'stdout','-l',ocr_lang],
                        capture_output=True,text=True,timeout=ocr_timeout)
                except subprocess.TimeoutExpired:
                    record['ocr_success']=False
                    record['ocr_error']=f'OCR timed out after {ocr_timeout} seconds'
                    proc=None
                if proc is not None:
                    record['ocr_text_characters']=len(proc.stdout.strip()) if proc.returncode==0 else 0
                    record['ocr_success']=proc.returncode==0
                    record['ocr_error']=proc.stderr[-200:] if proc.returncode else ''
        else:
            record['ocr_success']=False
            record['ocr_error']='Tesseract unavailable'
        record['chart_candidate']=bool(record['vector_drawings']>=12 or record['image_objects']>0)
        record['chart_semantics_verified']=False
        (out/f'page-{index+1:04}.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
        result.append(record)
    doc.close()
    return result

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('pdf');parser.add_argument('--out',required=True)
    args=parser.parse_args();print(json.dumps({'pages':len(inspect_pdf(args.pdf,args.out))}))
