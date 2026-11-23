#!/usr/bin/env python3
"""Offline integration test: cross-source aggregation, provenance and publication gate."""
import json, tempfile
from pathlib import Path
import research_pipeline as rp
from research_pipeline import build_knowledge, draft_lesson, draft_all, vision_pdf, research_claim
from free_visual import inspect_pdf
from free_research import make_packet, draft

def main():
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp);ev=root/'evidence';ev.mkdir()
        for sha,topics in [('a'*40,['candlestick','trend']),('b'*40,['candlestick'])]:
            (ev/(sha+'.json')).write_text(json.dumps({'source_sha':sha,'source_name':sha+'.pdf',
                'topics':[{'concept':x,'evidence_locations':[{'location':'page-1','term_mentions':1}]} for x in topics]}))
        packet=make_packet([{'location':'page-3','text':'A doji 十字星 has an open and close near each other.'}],'a'*40,'fixture.pdf')
        # Source passage locators must remain non-copyrighted and reproducible.
        assert all('excerpt_sha256' in row and 'location' in row
                   for rows in packet['topics'].values() for row in rows)
        assert 'doji' in packet['topics'] and packet['topics']['doji'][0]['location']=='page-3'
        preview=draft(packet,'doji')
        assert 'NOT FOR PUBLICATION' in preview and 'page-3' in preview
        catalog=root/'catalog.json'; result=build_knowledge(ev,catalog)
        assert len(result['topics'])==2
        assert len(result['topics']['candlestick']['sources'])==2
        assert result['verified_claims']==0
        lesson=root/'lesson.md'
        draft_lesson('candlestick',catalog,lesson)
        assert lesson.exists() and 'Candlestick' in lesson.read_text()
        assert 'source' in lesson.read_text().lower()
        manifest=draft_all(catalog,root/'outlines')
        assert len(manifest['generated_outlines'])==2
        assert not manifest['blocked_topics']
        assert (root/'outlines/manifest.json').exists()
        # Exercise actual page rendering, model message construction and persistence without API spend.
        try:
            import fitz
            pdf=root/'chart.pdf'; doc=fitz.open(); page=doc.new_page()
            page.draw_line((40,80),(40,180));page.draw_rect(fitz.Rect(30,110,50,150))
            doc.save(pdf);doc.close()
            previous=rp.call_model
            rp.call_model=lambda messages,model='gpt-4.1',max_tokens=3000: json.dumps({'page':1,'charts':[{'type':'candlestick'}],'uncertain_details':[]})
            free=inspect_pdf(pdf,root/'free-vision')
            assert len(free)==1 and free[0]['status']=='visual_features_extracted_unverified'
            assert free[0]['visual_coverage_complete'] is True
            # Real PyMuPDF rendering on a two-page fixture; no model verification implied.
            import os
            multi=root/'multi.pdf';d=fitz.open();d.new_page();d.new_page();d.save(multi);d.close()
            # Timeout fixture must contain real graphical marks: truly blank pages
            # intentionally bypass OCR and must never be counted as OCR timeouts.
            timeout_pdf=root/'ocr-timeout-fixture.pdf';tdoc=fitz.open()
            for _ in range(2):
                tp=tdoc.new_page();tp.draw_rect(fitz.Rect(60,80,120,180))
            tdoc.save(timeout_pdf);tdoc.close()
            old_limit=os.environ.get('TMM_VISUAL_MAX_PAGES')
            os.environ['TMM_VISUAL_MAX_PAGES']='1'
            try:
                sample=inspect_pdf(multi,root/'bounded-visual')
                assert len(sample)==1 and sample[0]['document_total_pages']==2
                assert sample[0]['visual_coverage_complete'] is False
            finally:
                if old_limit is None: os.environ.pop('TMM_VISUAL_MAX_PAGES',None)
                else: os.environ['TMM_VISUAL_MAX_PAGES']=old_limit
            # Confirm configured OCR deadline reaches the actual subprocess call.
            import free_visual as fv
            old_run=fv.subprocess.run
            old_which=fv.shutil.which
            old_timeout=os.environ.get('TMM_OCR_PAGE_TIMEOUT_SECONDS')
            try:
                os.environ['TMM_OCR_PAGE_TIMEOUT_SECONDS']='3'
                fv.shutil.which=lambda cmd: '/usr/bin/tesseract' if cmd=='tesseract' else old_which(cmd)
                calls=[]
                def fake_run(args,**kwargs):
                    if '--list-langs' in args:
                        return type('R',(),{'stdout':'eng','returncode':0,'stderr':''})()
                    calls.append(kwargs.get('timeout'))
                    raise fv.subprocess.TimeoutExpired(args,kwargs.get('timeout'))
                fv.subprocess.run=fake_run
                timed=inspect_pdf(timeout_pdf,root/'ocr-timeout')
                assert calls==[3,3] and all(not row['ocr_success'] for row in timed)
                assert all('3 seconds' in row['ocr_error'] for row in timed)
            finally:
                fv.subprocess.run=old_run
                fv.shutil.which=old_which
                if old_timeout is None: os.environ.pop('TMM_OCR_PAGE_TIMEOUT_SECONDS',None)
                else: os.environ['TMM_OCR_PAGE_TIMEOUT_SECONDS']=old_timeout
            images=vision_pdf(pdf,root/'vision')
            assert len(images)==1 and images[0]['human_review_complete'] is False
            assert (root/'vision/page-0001.json').exists()
            rp.call_model=previous
        except ImportError:
            print('SKIP: PyMuPDF not installed; vision fixture requires workflow environment')
        # Mock independent research response transport, preserving unverified gate.
        import urllib.request
        original=urllib.request.urlopen
        original_key=rp.os.environ.get('OPENAI_API_KEY')
        rp.os.environ['OPENAI_API_KEY']='test-placeholder'
        class FakeResponse:
            def __enter__(self): return self
            def __exit__(self,*args): return False
            def read(self,*args): return b'{"output":[{"type":"message","content":[{"text":"Independent reference: example.com"}]}]}'
        urllib.request.urlopen=lambda *args,**kwargs: FakeResponse()
        try:
            record=research_claim('A doji has similar open and close','a'*40,'page-1',root/'fact.json')
            assert record['verified'] is False and record['reviewer_approved'] is False
            assert (root/'fact.json').exists()
        finally:
            urllib.request.urlopen=original
            if original_key is None: rp.os.environ.pop('OPENAI_API_KEY',None)
            else: rp.os.environ['OPENAI_API_KEY']=original_key
        print('PASS: source aggregation, vision page processing, fact-check transport and publication gate')
if __name__=='__main__':main()
