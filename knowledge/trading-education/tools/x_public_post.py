#!/usr/bin/env python3
"""Read known public X Posts through X's oEmbed endpoint."""

import argparse
from html.parser import HTMLParser
import json
import re
import sys
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode, urlsplit
from urllib.request import urlopen

HOSTS = {"x.com", "www.x.com", "twitter.com", "www.twitter.com",
         "mobile.twitter.com"}
POST_PATH = re.compile(r"/(?:[A-Za-z0-9_]{1,15}|i/web)/status/([0-9]{1,20})/?")
OEMBED = "https://publish.twitter.com/oembed"


class PostHTML(HTMLParser):
    """Extract the visible post text and timestamp label from a rich embed."""

    def __init__(self, post_id):
        super().__init__()
        self.post_id = post_id
        self.in_text = False
        self.in_date = False
        self.language = None
        self.text = []
        self.date = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "p" and not self.text:
            self.in_text = True
            self.language = attrs.get("lang")
        elif tag == "br" and self.in_text:
            self.text.append("\n")
        elif tag == "a" and not self.in_text:
            path = urlsplit(attrs.get("href", "")).path
            self.in_date = path.rstrip("/").endswith("/status/" + self.post_id)

    def handle_endtag(self, tag):
        if tag == "p":
            self.in_text = False
        elif tag == "a":
            self.in_date = False

    def handle_data(self, data):
        if self.in_text:
            self.text.append(data)
        elif self.in_date:
            self.date.append(data)


def read_post(url):
    parts = urlsplit(url)
    match = POST_PATH.fullmatch(parts.path)
    if parts.scheme != "https" or parts.netloc.lower() not in HOSTS or not match:
        raise ValueError("Expected a public https://x.com/<handle>/status/<id> URL")

    post_id = match.group(1)
    canonical_input = "https://x.com" + parts.path.rstrip("/")
    params = urlencode({"url": canonical_input, "omit_script": 1})
    with urlopen(f"{OEMBED}?{params}", timeout=20) as response:
        result = json.load(response)

    if result.get("type") != "rich" or not result.get("html"):
        raise ValueError("X returned no readable public embed")
    returned_path = urlsplit(result.get("url", "")).path
    if returned_path.rstrip("/").split("/")[-1] != post_id:
        raise ValueError("X returned a different post ID")

    embed = PostHTML(post_id)
    embed.feed(result["html"])
    post_text = "".join(embed.text).strip()
    if not post_text:
        raise ValueError("X returned an embed without readable post text")

    return {
        "id": post_id,
        "url": result["url"],
        "author": result.get("author_name"),
        "author_url": result.get("author_url"),
        "language": embed.language,
        "date_label": "".join(embed.date).strip() or None,
        "text": post_text,
        "public_metrics": None,
        "source": "X public oEmbed",
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("urls", nargs="+", help="One or more public X post URLs")
    args = parser.parse_args()
    failed = False
    for url in args.urls:
        try:
            print(json.dumps(read_post(url), ensure_ascii=False))
        except (HTTPError, URLError, TimeoutError, ValueError) as error:
            failed = True
            print(f"{url}: {error}", file=sys.stderr)
    return int(failed)


if __name__ == "__main__":
    sys.exit(main())
