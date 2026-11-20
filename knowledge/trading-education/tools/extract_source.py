#!/usr/bin/env python3
"""Extract DOCX/PPTX/PDF text with source locations and image inventories.
Requires Python 3.10+; PDF requires: pip install pymupdf.
This is mechanical extraction, NOT visual verification or factual validation.
Do not commit extracted third-party text into a public repository.
"""
import argparse, hashlib, json, re, zipfile, shutil, subprocess, tempfile
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

def pdf(path):
    try: import fitz
    except ImportError: raise SystemExit('Install PDF support: pip install pymupdf')
    d=fitz.open(path); blocks=[]; images=[]; blank=[]; ocr_pages=[]
    for i,p in enumerate(d,1):
        s=p.get_text('text').strip()
        if s: blocks.append({'location':f'page-{i}','text':s})
        else:
            blank.append(i)
            if shutil.which('tesseract') and len(ocr_pages)<3:
                with tempfile.TemporaryDirectory() as tmp:
                    image_path=Path(tmp)/'page.png'
                    image_path.write_bytes(p.get_pixmap(matrix=fitz.Matrix(2,2)).tobytes('png'))
                    run=subprocess.run(['tesseract',str(image_path),'stdout','-l','eng+chi_sim'],
                                       capture_output=True,text=True,timeout=15)
                    if run.returncode==0 and run.stdout.strip():
                        blocks.append({'location':f'page-{i}:OCR-unverified',
                                       'text':run.stdout.strip()})
                        ocr_pages.append(i)
        for j,im in enumerate(p.get_images(full=True),1):
            images.append({'location':f'page-{i}:image-{j}',
                           'xref':im[0],'visually_verified':False})
    return blocks,images,{'pages':len(d),'pages_without_extractable_text':blank, 'ocr_pages':ocr_pages, 'ocr_limit_pages':3, 'ocr_requires_manual_review':True}

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
