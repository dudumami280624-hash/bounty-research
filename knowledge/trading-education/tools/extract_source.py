#!/usr/bin/env python3
"""Extract DOCX/PPTX/PDF text with source locations and image inventories.
Requires Python 3.10+; PDF requires: pip install pymupdf.
This is mechanical extraction, NOT visual verification or factual validation.
Do not commit extracted third-party text into a public repository.
"""
import argparse, hashlib, json, re, zipfile, shutil, subprocess, tempfile, os
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
      'a':'http://schemas.openxmlformats.org/drawingml/2006/main',
      'p':'http://schemas.openxmlformats.org/presentationml/2006/main'}

def ooxml(path, fmt):
    blocks, images = [], []
    with zipfile.ZipFile(path) as z:
        names=z.namelist()
        if fmt=='docx':
            parts=[n for n in names if n=='word/document.xml' or re.fullmatch(r'word/(header|footer)\d+\.xml',n)]
            parts.sort(key=lambda n:(n!='word/document.xml',n))
        else:
            parts=sorted((n for n in names if re.fullmatch(r'ppt/slides/slide\d+\.xml',n)),
                         key=lambda n:int(re.search(r'slide(\d+)',n).group(1)))
        for part in parts:
            root=ET.fromstring(z.read(part))
            if fmt=='docx':
                for i,p in enumerate(root.findall('.//w:p',NS),1):
                    s=''.join(t.text or '' for t in p.findall('.//w:t',NS)).strip()
                    if s: blocks.append({'location':f'{part}:paragraph-{i}','text':s})
            else:
                slide=int(re.search(r'slide(\d+)',part).group(1))
                for i,shape in enumerate(root.findall('.//p:sp',NS),1):
                    paras=[''.join(t.text or '' for t in p.findall('.//a:t',NS))
                           for p in shape.findall('.//a:p',NS)]
                    s='\n'.join(p for p in paras if p.strip()).strip()
                    if s: blocks.append({'location':f'slide-{slide}:shape-{i}','text':s})
        prefix='word/media/' if fmt=='docx' else 'ppt/media/'
        for n in names:
            if n.startswith(prefix) and not n.endswith('/'):
                b=z.read(n)
                images.append({'internal_path':n,'bytes':len(b),
                               'sha256':hashlib.sha256(b).hexdigest(),
                               'visually_verified':False})
    return blocks, images, {'xml_parts_read':parts}

def pdf(path, start_page=0, max_pages=None):
    try: import fitz
    except ImportError: raise SystemExit('Install PDF support: pip install pymupdf')
    d=fitz.open(path); blocks=[]; images=[]; blank=[]; ocr_pages=[]; ocr_failed_pages=[]
    # A page OCR must not exhaust the per-document 90-second watchdog.
    ocr_timeout=max(3,min(30,int(os.environ.get('TMM_OCR_PAGE_TIMEOUT_SECONDS','12'))))
    # Bound expensive OCR on initial extraction; remaining blank pages stay explicitly pending.
    max_ocr_pages=max(0,int(os.environ.get('TMM_INITIAL_OCR_MAX_PAGES','4')))
    attempted_ocr=0
    deferred_ocr_pages=[]
    languages='eng'
    if shutil.which('tesseract'):
        try:
            available=subprocess.run(['tesseract','--list-langs'],capture_output=True,text=True,timeout=5).stdout
            if 'chi_sim' in available.split(): languages='eng+chi_sim'
        except (subprocess.TimeoutExpired,OSError): pass
    total_pages=len(d)
    stop=total_pages if max_pages is None else min(total_pages,start_page+max_pages)
    if start_page<0 or start_page>total_pages: raise ValueError('Invalid PDF start page')
    for i in range(start_page,stop):
        p=d[i]
        page_number=i+1
        s=p.get_text('text').strip()
        if s: blocks.append({'location':f'page-{page_number}','text':s})
        else:
            blank.append(page_number)
            if attempted_ocr >= max_ocr_pages:
                deferred_ocr_pages.append(page_number)
                ocr_failed_pages.append(page_number)
            elif shutil.which('tesseract'):
                attempted_ocr+=1
                with tempfile.TemporaryDirectory() as tmp:
                    image_path=Path(tmp)/'page.png'
                    image_path.write_bytes(p.get_pixmap(matrix=fitz.Matrix(2,2)).tobytes('png'))
                    try:
                        run=subprocess.run(['tesseract',str(image_path),'stdout','-l',languages],
                                           capture_output=True,text=True,timeout=ocr_timeout)
                        if run.returncode==0 and run.stdout.strip():
                            blocks.append({'location':f'page-{page_number}:OCR-unverified',
                                           'text':run.stdout.strip()})
                            ocr_pages.append(page_number)
                        else: ocr_failed_pages.append(page_number)
                    except (subprocess.TimeoutExpired, OSError): ocr_failed_pages.append(page_number)
            else: ocr_failed_pages.append(page_number)
        for j,im in enumerate(p.get_images(full=True),1):
            images.append({'location':f'page-{page_number}:image-{j}',
                           'xref':im[0],'visually_verified':False})
    return blocks,images,{'pages':total_pages,'window_start_page':start_page+1,'window_end_page':stop,'window_complete':stop>=total_pages,'pages_without_extractable_text':blank, 'ocr_pages':ocr_pages, 'ocr_failed_pages':ocr_failed_pages, 'ocr_deferred_pages':deferred_ocr_pages, 'initial_ocr_page_limit':max_ocr_pages, 'ocr_languages':languages, 'ocr_page_timeout_seconds':ocr_timeout, 'ocr_requires_manual_review':True}

def main():
    a=argparse.ArgumentParser()
    a.add_argument('source');a.add_argument('--out',required=True)
    args=a.parse_args();src=Path(args.source);out=Path(args.out)
    out.mkdir(parents=True,exist_ok=True)
    fmt=src.suffix.lower().lstrip('.')
    if fmt in ('docx','pptx'):blocks,images,details=ooxml(src,fmt)
    elif fmt=='pdf':blocks,images,details=pdf(src)
    else:raise SystemExit('Unsupported format; .doc/.ppt require conversion')
    manifest={'source_name':src.name,
              'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),
              'format':fmt,'extraction_pass_completed':True,
              'full_content_verified':False,'visual_review_complete':False,
              'text_blocks':len(blocks),'images_found':len(images),
              'details':details}
    (out/'extracted_text.md').write_text('\n\n'.join(
        f"### {b['location']}\n{b['text']}" for b in blocks)+'\n',encoding='utf-8')
    (out/'image_inventory.json').write_text(
        json.dumps(images,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'manifest.json').write_text(
        json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
    print(json.dumps(manifest,ensure_ascii=False))
if __name__=='__main__':main()
