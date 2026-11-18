---
name: trading-education-multisource-search
description: Read-only, citation-first search routing for the trading-education stock knowledge base, ChatGPT Library source archives, GitHub repository and optional Agent Reach/QMD.
---

# trading-education 多源只读搜索

## Boundaries (mandatory)
- Single stable knowledge base name: `trading-education`.
- **Stage 1 audit only.** Never modify `main`, delete, move, archive, merge, publish full copyrighted source files, or execute stage 2 without fresh explicit approval.
- Do not assume a SKILL.md, workflow YAML, ZIP listing, or index proves installed tools, completed extraction, or full reading.
- Keep `knowledge/market-psychology/` as an independent traceable source until the user approves any future migration.
- Do not silently send privately backed-up originals to public APIs or external search services.

## Retrieval routing
1. **Repository inventory:** read GitHub recursive tree at the pinned commit; enumerate all paths and classify by *actual content*. Include `knowledge/trading-education/`, `knowledge/market-psychology/`, relevant data and research skill locations. Exclude unrelated bounty-hunting and film assets after inspecting ambiguous file references.
2. **Private sources:** locate files in ChatGPT Library folder `/trading-education/`: two original ZIPs and the 98-file comparison JSON. Report 'found' only after listing; report 'opened' and 'hash verified' only after separate completed checks. Handle the ZIPs in an authorized private working environment. Preserve filenames and source hashes.
3. **Text retrieval:** prefer already-readable Markdown/TXT and source records; search using exact terms, synonyms, and topic concepts. If available, use QMD in a private/local environment for keyword and semantic lookup; it is optional, not a prerequisite. Never claim QMD is installed before a successful version/status check.
4. **External public research:** use existing web/GitHub tools first; Agent Reach may route public website/video/social content only when its doctor result confirms channels. External observations must be attributed separately and must never be merged into user-uploaded source-only content without permission.
5. **Evidence mapping:** use `source-ingestion-and-citation` to record source filename, hash, path, page/slide/paragraph, direct quotation location, claim, date and reading coverage.
6. **Compare:** use `evidence-conflict-resolver` workflow where accessible; exact match, paragraph containment, near-match, and thematic overlap are separate labels. Graphical/slide differences require visual review. Preserve opposing stop-loss criteria (e.g. 10.03 speech P17 versus P24) as **存疑** rather than silently adjudicating.

## Example query plan
For 'find all stop-loss rules and contradictions':
- Search `止损|卖出|止盈|收盘价|触及|stop loss|exit|disposition` in both knowledge directories and privately available originals.
- Return a deduplicated evidence ledger with all original source pointers, differences, exceptions, and verification status; do not invent missing pages.

## Required output
- Snapshot: repository SHA, search date, searched collections, tool/connector health.
- Source ledger: `file_path | filename | format | source_kind(original/extract/index/card/draft) | read_status(full/partial/index-only/unreadable) | page_or_paragraph | hash/status`.
- Repetition: matched passage locations from **both** files; unique paragraphs, figures and notes.
- Conflicts: all competing statements and source positions, marked **存疑**.
- Separate output section for external facts and their dates.
- Stage 1 report only; proposed taxonomy is not an approved file move.

## Optional QMD private indexing (not auto-executed)
Official upstream: https://github.com/tobi/qmd ; install documentation: `npm install -g @tobilu/qmd`.
QMD indexes readable text/Markdown; convert DOC/DOCX/PDF/PPTX privately first and preserve page/slide anchors. Avoid GitHub-hosted indexing of user-private ZIPs. Installing QMD or downloading model weights requires separate resource/privacy approval before running.
