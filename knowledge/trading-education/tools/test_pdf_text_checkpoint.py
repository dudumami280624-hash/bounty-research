#!/usr/bin/env python3
"""Synthetic cross-run page metadata regression. Never writes textbook content."""
import json
import hashlib
import tempfile
from pathlib import Path
import fitz
import run_extraction_batch as batch

def main():
    with tempfile.TemporaryDirectory() as td:
        td=Path(td)
        doc=fitz.open()
        for i in range(5):
            p=doc.new_page()
            if i!=2:
                p.insert_text((72,72),f'SYNTHETIC PRIVATE PAGE {i+1}')
        source=td/'fixture.pdf'
        doc.save(source)
        data=source.read_bytes()
        batch.STATE=td/'state.json'
        batch.download_blob=lambda sha, timeout_seconds=180:data
        entry={'name':'synthetic.pdf','sha':'a'*40,'category':'01-test'}
        files={entry['sha']:{'extraction_status':'partial_ocr_failure'}}
        first=batch.advance_pdf_text_windows([entry],files,budget_seconds=10,window_pages=2)
        assert first[0]['pages']=='1-2',first
        persisted=json.loads(batch.STATE.read_text())['files']
        assert persisted[entry['sha']]['pdf_text_page_audit']['next_page']==2
        second=batch.advance_pdf_text_windows([entry],persisted,budget_seconds=10,window_pages=2)
        assert second[0]['pages']=='3-4',second
        third=batch.advance_pdf_text_windows([entry],persisted,budget_seconds=10,window_pages=2)
        assert third[0]['pages']=='5-5',third
        audit=persisted[entry['sha']]['pdf_text_page_audit']
        assert audit['coverage_complete'] and audit['next_page']==5
        assert audit['source_sha256']==hashlib.sha256(data).hexdigest()
        assert audit['page_evidence']['3']['ocr_needed']
        assert audit['page_evidence']['1']['text_origin']=='embedded_pdf_text'
        assert not any('SYNTHETIC PRIVATE PAGE' in str(v) for v in audit['page_evidence'].values())
        assert not batch.advance_pdf_text_windows([entry],persisted,budget_seconds=10,window_pages=2)
        assert all(not v['verified'] for v in audit['page_evidence'].values())
        # Tampering with source bytes must not advance a cursor or replace evidence.
        persisted[entry['sha']]['pdf_text_page_audit']['coverage_complete']=False
        persisted[entry['sha']]['pdf_text_page_audit']['next_page']=4
        batch.download_blob=lambda sha, timeout_seconds=180: b'changed bytes'
        assert not batch.advance_pdf_text_windows([entry],persisted,budget_seconds=10,window_pages=2)
        assert persisted[entry['sha']]['pdf_text_page_audit']['next_page']==4
        assert 'source SHA-256' in persisted[entry['sha']]['pdf_text_page_audit']['last_error']
    print('PASS synthetic cross-run PDF text metadata checkpoint; no copyrighted text persisted')

if __name__=='__main__':
    main()
