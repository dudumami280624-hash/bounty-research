# The Market Mind — evidence-first X editorial workflow (BlueV feature study)

Updated: 2026-11-23. Status: documented workflow; NOT an integrated BlueV API, live automation, or published post.

For multilingual topic discovery, comparison with published posts, and article/thread review, use the [global X research and review workflow](X-GLOBAL-RESEARCH-AND-REVIEW.md).

## Public feature observations
BlueV's publicly visible rewrite page at https://bluev.fun/rewrite offers: input text or URLs, multi-link synthesis, angle generation, writing style, target length, extra instructions, rewrite, image generation, and X publishing controls. These are interface observations, not evidence that logged-in features or APIs work. Do not scrape private endpoints or reuse BlueV proprietary text/code.

## The Market Mind editorial pipeline
1. **Collect**: store canonical primary-source URL, publisher, publication date, retrieved date, and a short paraphrase. Record secondary corroboration separately.
2. **Verify**: label each claim VERIFIED / REPORTED-UNCONFIRMED / DISPUTED / UNKNOWN, with source URL and evidence excerpt locator. Check market price moves against dated price data before writing that a stock fell because of a story.
3. **Angle**: draft 3 accurate, restrained headlines (question, market impact, and factual development). Never claim causation without evidence.
4. **Interpret**: clearly separate source-reported facts from the author's own analysis. Explain plausible bullish and bearish implications and what would change the thesis; avoid price targets without a documented model.
5. **Write**: natural American English, compact X-first copy; default 100–170 words including title, with a short source link and 3–5 relevant tags. Do not translate Chinese literally.
6. **Review**: ensure names, dates, amounts, units, company affiliations, quotes, and regulatory/legal status match sources. No guilt-by-association or treating allegations as convictions. Never use an unverified headline as a fact.
7. **Deliver**: create a DRAFT only. Publication to X requires explicit separate user authorization. Save links/versions only after verified posting.

## Ready-to-use prompt
> Using the source URLs and verified claim ledger below, draft one original X post in natural American English. Use a compelling but non-sensational question headline. Keep it 100–170 words, distinguish reporting from analysis, include one balanced market implication, cite the primary source with date and URL, and end with 3–5 relevant hashtags. Do not invent market movements, criminal findings, insider knowledge, or facts not supported by the ledger. If evidence is insufficient, flag what must be checked instead of guessing.

## Quality gates (all must pass)
- [ ] Source is accessible or clearly marked inaccessible; original outlet and date are attributed accurately.
- [ ] Each material fact has an evidence locator; disputed allegations are attributed.
- [ ] Numerical claims, ticker symbols, and market moves independently checked where relevant.
- [ ] Title is interesting but not exaggerated; no invented causality.
- [ ] Author analysis explicitly labeled, not presented as reported fact.
- [ ] No unattributed copied prose; original writing.
- [ ] No automatic publication.

## Example restrained headline
**Could NVIDIA Face More Pressure? A Financial Times Investigation Raises Questions**

This is an illustrative editorial headline only, not a verified forecast or a claim that the investigation moved NVDA stock.

## Next engineering step
Prototype a local, free-source Markdown claim-ledger + draft validator, using synthetic fixtures first; do not conflate a passing text check with independent fact verification. Keep it isolated from the 178-source extraction pipeline and existing scheduled tasks until tested.
