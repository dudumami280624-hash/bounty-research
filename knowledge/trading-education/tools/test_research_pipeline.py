#!/usr/bin/env python3
"""Offline integration test: cross-source aggregation, provenance and publication gate."""
import json, tempfile
from pathlib import Path
import research_pipeline as rp
from research_pipeline import build_knowledge, draft_lesson, vision_pdf, research_claim

def main():
    with tempfile.TemporaryDirectory() as tmp:
        root=Path(tmp);ev=root/'evidence';ev.mkdir()
        for sha,topics in [('a'*40,['candlestick','trend']),('b'*40,['candlestick'])]:
            (ev/(sha+'.json')).write_text(json.dumps({'source_sha':sha,'source_name':sha+'.pdf',
                'topics':[{'concept':x,'evidence_locations':[{'location':'page-1','term_mentions':1}]} for x in topics]}))
        catalog=root/'catalog.json'; result=build_knowledge(ev,catalog)
        assert len(result['topics'])==2
        assert len(result['topics']['candlestick']['sources'])==2
        assert result['verified_claims']==0
        try: draft_lesson('candlestick',catalog,root/'lesson.md')
        except RuntimeError as exc: assert 'publication blocked' in str(exc)
        else: raise AssertionError('Unverified lesson was incorrectly allowed')
        assert not (root/'lesson.md').exists()
        # Exercise actual page rendering, model message construction and persistence without API spend.
        try:
            import fitz
            pdf=root/'chart.pdf'; doc=fitz.open(); page=doc.new_page()
            page.draw_line((40,80),(40,180));page.draw_rect(fitz.Rect(30,110,50,150))
            doc.save(pdf);doc.close()
            previous=rp.call_model
            rp.call_model=lambda messages,model='gpt-4.1',max_tokens=3000: json.dumps({'page':1,'charts':[{'type':'candlestick'}],'uncertain_details':[]})
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
