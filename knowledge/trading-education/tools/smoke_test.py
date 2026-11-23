#!/usr/bin/env python3
"""Synthetic offline smoke tests: never uses or publishes original教材 content."""
import tempfile, zipfile
from pathlib import Path
import fitz
from extract_source import ooxml, pdf
from run_extraction_batch import inventory
from free_visual import inspect_pdf

def main():
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp)
        doc=root/'fixture.docx'
        with zipfile.ZipFile(doc,'w') as z:
            z.writestr('word/document.xml',
              '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body><w:p><w:r><w:t>DOCX_TEST_OK</w:t></w:r></w:p></w:body></w:document>')
        blocks,_,_=ooxml(doc,'docx')
        assert any('DOCX_TEST_OK' in x['text'] for x in blocks),blocks
        ppt=root/'fixture.pptx'
        with zipfile.ZipFile(ppt,'w') as z:
            z.writestr('ppt/slides/slide1.xml',
              '<p:sld xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main"><p:cSld><p:spTree><p:sp><p:txBody><a:p><a:r><a:t>PPTX_TEST_OK</a:t></a:r></a:p></p:txBody></p:sp></p:spTree></p:cSld></p:sld>')
        blocks,_,_=ooxml(ppt,'pptx')
        assert any('PPTX_TEST_OK' in x['text'] for x in blocks),blocks
        path=root/'fixture.pdf';d=fitz.open();p=d.new_page();p.insert_text((50,50),'PDF_TEST_OK');d.save(path);d.close()
        blocks,_,details=pdf(path)
        assert any('PDF_TEST_OK' in x['text'] for x in blocks),blocks
        assert details['pages']==1
        multi=root/'multipage.pdf';d=fitz.open()
        for n in range(4):
            page=d.new_page();page.insert_text((50,50),f'PAGE_{n+1}')
        d.save(multi);d.close()
        import os
        os.environ['TMM_VISUAL_MAX_PAGES']='2'
        first=inspect_pdf(multi,root/'visual-first',start_page=0)
        second=inspect_pdf(multi,root/'visual-second',start_page=2)
        assert [x['page'] for x in first]==[1,2]
        assert [x['page'] for x in second]==[3,4]
        assert first[0]['visual_coverage_complete'] is False
        assert second[0]['visual_coverage_complete'] is False
        assert second[-1]['visual_coverage_complete'] is True
        import json
        saved=json.loads((root/'visual-second'/'page-0004.json').read_text(encoding='utf-8'))
        assert saved['visual_coverage_complete'] is True
        earlier=json.loads((root/'visual-second'/'page-0003.json').read_text(encoding='utf-8'))
        assert earlier['visual_coverage_complete'] is False
        os.environ.pop('TMM_VISUAL_MAX_PAGES',None)
    print('PASS: DOCX, PPTX, PDF extraction smoke tests')
if __name__=='__main__':main()
