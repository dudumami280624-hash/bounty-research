#!/usr/bin/env python3
"""Free offline visual inspection using PyMuPDF and Tesseract.
Produces page-image evidence and OCR; does NOT claim semantic chart understanding.
"""
import hashlib, json, shutil, subprocess, tempfile
from pathlib import Path

def inspect_pdf(pdf_path, output):
    import fitz
    doc=fitz.open(pdf_path);out=Path(output);out.mkdir(parents=True,exist_ok=True)
    langs=subprocess.run(['tesseract','--list-langs'],capture_output=True,text=True).stdout if shutil.which('tesseract') else ''
    ocr_lang='eng+chi_sim' if 'chi_sim' in langs else 'eng'
    result=[]
    for index,page in enumerate(doc):
        pix=page.get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False)
        png=pix.tobytes('png')
        record={'page':index+1,'render_sha256':hashlib.sha256(png).hexdigest(),
                'image_objects':len(page.get_images(full=True)),
                'vector_drawings':len(page.get_drawings()),
                'status':'visual_features_extracted_unverified'}
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
                        capture_output=True,text=True,timeout=30)
                except subprocess.TimeoutExpired:
                    record['ocr_success']=False
                    record['ocr_error']='OCR timed out after 30 seconds'
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
    return result

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('pdf');parser.add_argument('--out',required=True)
    args=parser.parse_args();print(json.dumps({'pages':len(inspect_pdf(args.pdf,args.out))}))
