#!/usr/bin/env python3
"""Free offline visual inspection using PyMuPDF and Tesseract.
Produces page-image evidence and OCR; does NOT claim semantic chart understanding.
"""
import hashlib, json, shutil, subprocess, tempfile
from pathlib import Path

def inspect_pdf(pdf_path, output):
    import fitz
    doc=fitz.open(pdf_path);out=Path(output);out.mkdir(parents=True,exist_ok=True)
    result=[]
    for index,page in enumerate(doc):
        pix=page.get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False)
        png=pix.tobytes('png')
        record={'page':index+1,'render_sha256':hashlib.sha256(png).hexdigest(),
                'image_objects':len(page.get_images(full=True)),
                'vector_drawings':len(page.get_drawings()),
                'status':'visual_features_extracted_unverified'}
        if shutil.which('tesseract'):
            with tempfile.TemporaryDirectory() as td:
                image=Path(td)/'page.png';image.write_bytes(png)
                proc=subprocess.run(['tesseract',str(image),'stdout','-l','eng+chi_sim'],
                    capture_output=True,text=True,timeout=120)
                record['ocr_text_characters']=len(proc.stdout.strip()) if proc.returncode==0 else 0
                record['ocr_success']=proc.returncode==0
        else: record['ocr_success']=False
        (out/f'page-{index+1:04}.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
        result.append(record)
    return result

if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('pdf');parser.add_argument('--out',required=True)
    args=parser.parse_args();print(json.dumps({'pages':len(inspect_pdf(args.pdf,args.out))}))
