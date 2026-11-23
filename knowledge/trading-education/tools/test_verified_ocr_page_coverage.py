#!/usr/bin/env python3
"""Synthetic regression only; does not validate original textbooks."""
from resume_visual_pages import verified_ocr_page_coverage

def test():
    good={'total_pages':2,'page_evidence':{
        '1':{'render_sha256':'a'*64,'ocr_actual_success':True},
        '2':{'render_sha256':'b'*64,'embedded_text_available':True}}}
    assert verified_ocr_page_coverage(good)
    assert not verified_ocr_page_coverage({'total_pages':2,'page_evidence':{'1':good['page_evidence']['1']}})
    assert not verified_ocr_page_coverage({'total_pages':2,'page_evidence':{
        '1':good['page_evidence']['1'],'2':{'render_sha256':'b'*64}}})
    assert not verified_ocr_page_coverage({'total_pages':2,'page_evidence':{
        '1':good['page_evidence']['1'],'2':{'render_sha256':'bad','ocr_actual_success':True}}})
    print('PASS: missing/unresolved/invalid page evidence cannot certify OCR completion')

if __name__=='__main__':
    test()
