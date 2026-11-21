#!/usr/bin/env python3
"""Real process-isolation regression; synthetic worker, not textbook validation."""
import os, sys, time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
import run_extraction_batch as batch

def slow_extract(entry, blob):
    time.sleep(5)
    return {'extraction_status':'extracted'}

def fast_extract(entry, blob):
    return {'extraction_status':'extracted'}

def fake_download(sha):
    return b'test'

def main():
    batch.download_blob=fake_download
    batch.extract=slow_extract
    started=time.monotonic()
    try:
        batch.isolated_extract({'sha':'fixture'},1)
        raise AssertionError('Timeout not enforced')
    except TimeoutError:
        pass
    assert time.monotonic()-started<4, 'Hard deadline exceeded'
    batch.extract=fast_extract
    assert batch.isolated_extract({'sha':'fixture'},3)['extraction_status']=='extracted'
    print('Process isolation timeout and success regressions passed (synthetic only)')

if __name__=='__main__': main()
