"""Offline-safe Scrapling installation smoke test; does not scrape third-party sites."""
from importlib.metadata import version
from scrapling import Selector

html = '<html><body><h1>Scrapling ready</h1></body></html>'
page = Selector(text=html)
heading = page.css('h1::text').get()
assert heading == 'Scrapling ready', heading
print(f"Scrapling {version('scrapling')} installed; local HTML parsing OK")
