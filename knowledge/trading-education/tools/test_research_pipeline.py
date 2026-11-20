#!/usr/bin/env python3
"""Offline integration test: cross-source aggregation, provenance and publication gate."""
import json, tempfile
from pathlib import Path
from research_pipeline import build_knowledge, draft_lesson

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
        print('PASS: cross-source catalog, SHA provenance and unverified publication gate')
if __name__=='__main__':main()
