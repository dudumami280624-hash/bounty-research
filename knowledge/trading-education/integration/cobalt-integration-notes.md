# Cobalt media intake — optional research component

Upstream: https://github.com/imputnet/cobalt (AGPL-3.0; verify current license and deployment requirements before hosting).

This module is intentionally **not** an automatic downloader. It prepares a permission-gated metadata queue for public, expressly authorized market education videos. The existing 178 textbook sources and first-26 candlestick priority remain unchanged.

1. Add candidates to a local JSON array (do not commit credentials or personal data), with `url`, `media_kind` (`market_chart` or `financial_education`), `permission` (`explicit_authorization` only when documented), and `permission_reference`.
2. Run `python tools/cobalt_media_gate.py candidates.json --out integration/cobalt-media-review.md` from `knowledge/trading-education`.
3. Review all eligible records and platform terms manually. The gate checks only declared metadata, not actual legal rights.
4. If authorized and technically supported, use a separately deployed cobalt service following upstream instructions. Do not bypass DRM, access restrictions, or platform safeguards.
5. Extract local frames using FFmpeg and annotate chart candidates using OpenCV/Tesseract; retain timecode, source URL, permission evidence, and independent verification status. Do not commit copyrighted video frames or audio to the public repository.

**Not yet implemented:** a deployed cobalt server, downloads, FFmpeg frame pipeline, real-world end-to-end integration, or verified chart semantics. No paid API required by this gate.
