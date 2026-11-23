# Mareader / Hayro evaluation for The Market Mind

Date: 2026-11-23. Status: upstream documentation inspected; integration NOT validated on actual textbook PDFs.

Upstream: https://github.com/codewiththiha/mareader (MIT first-party code; check dependency notices). README documents `cargo run -p mareader-cli -- render book.pdf --page 0 -o page0.png`, headless MCP, and Rust Hayro PDF parsing/rendering. This is a rasterization alternative, NOT OCR or independent financial fact verification.

## Bounded free evaluation gate
1. Choose one failing PDF page from priority-26 candlestick sources; keep copyrighted input and rendered output OUT of public Git history.
2. Record source identifier, page number, input SHA-256, parser failure class, runtime, output PNG SHA-256, and exit status only.
3. Compare existing PyMuPDF rasterization with Mareader CLI on the SAME page. Run in an isolated scratch directory with timeout and memory cap; do not install a Rust build into the main hourly extraction path yet.
4. Inspect legibility of candles, axes, annotations and Chinese/English labels; if rasterization succeeds, run actual installed Tesseract OCR separately, recording engine/language and confidence limitations.
5. Keep semantic chart interpretation and independent market-data verification as separate downstream gates. Never count a successful render or OCR as a verified lesson.
6. If Rust build or memory/time costs exceed hosted runner limits, evaluate direct Hayro CLI/library on a dedicated optional job or retain PyMuPDF; do not slow or block the existing 178-source queue.

## Acceptance criteria
- At least one actual previously failing textbook page, with source/page locator and reproducible exit codes.
- Comparative timing and image evidence kept private; public repository contains hashes, metadata, and code only.
- A passing real GitHub Actions run ID AFTER the change, not a synthetic fixture alone.
- No paid API and no automatic X/YouTube publication.

## Current blockers and next action
No actual failing PDF bytes were fetched or benchmarked in this evaluation; Hayro performance and compatibility are UNKNOWN. Next cycle: identify a priority-26 failure with available authorized source, run both renderers, and attach reproducible non-copyright evidence. Keep OCR queue processing in parallel.
