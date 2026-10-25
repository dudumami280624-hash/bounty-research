# Grill With Docs

## Purpose

审问 The Market Mind 的理论、章节、历史案例和英文成稿，并强制结合仓库资料。它组合 grill-me 的质询方式与市场心理资料库。

## Required reading

Before grilling, read:

- knowledge/market-psychology/PROJECT_RULES.md
- knowledge/market-psychology/THE_MARKET_MIND_CORE_SKELETON_v0.1.md
- knowledge/market-psychology/manifest.json
- knowledge/market-psychology/chanlun/manifest.json
- .agents/skills/market-psychology-western-writing/SKILL.md
- relevant source text under knowledge/market-psychology/

For US historical claims, retrieve current evidence from FRED, Federal Reserve, NBER, BLS, SEC, CBOE or other primary sources.

## Grilling procedure

1. State the exact claim or chapter being tested.
2. Separate SOURCE, MODEL, HISTORY, PSYCHOLOGY, ADAPTATION and UNVERIFIED.
3. Ask whether the claim is borrowed concept, new definition, analogy or empirical result.
4. Test the claim against at least one US bull phase, one bear phase and one failure or false-signal case.
5. Look for hindsight bias, survivorship bias, confirmation bias, data leakage, cherry-picking and terminology ambiguity.
6. Challenge whether the concept is understandable to a Western beginner without Chinese forum context.
7. Require an invalidation condition and a way to test the claim out of sample.
8. Reject publication-ready status when essential evidence is missing.

## Output

Return:

- Verdict: PASS / NEEDS REVISION / BLOCKED
- Strongest supported point
- Three hardest objections
- Evidence table with source and date
- Missing evidence
- Smallest repair
- Chinese explanation
- English wording if the text is being adapted for The Market Mind

## Boundaries

Do not present grilling as investment advice. Do not turn a passing theory review into a stock recommendation, price target or promise of returns. Keep original drafts and record revisions.


## Continuity lock

Before any new audit or X thread:

1. Read PROJECT_RULES.md and the saved X thread directory.
2. Identify the last saved thread ID and topic.
3. Check the new topic against the topic ledger and reject duplicates unless revision is requested.
4. Preserve Chinese review, English text, character counts, evidence labels and verdict.
5. Save the finished artifact before claiming PASS or completion.
6. If the repository write or verification fails, report the failure clearly.
