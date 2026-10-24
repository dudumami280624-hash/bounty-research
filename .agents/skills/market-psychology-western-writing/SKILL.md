---
name: market-psychology-western-writing
description: Convert Chinese market psychology, trading, macroeconomics, and Chanlun source materials into psychologically credible English content for Western investors on X, short video, and newsletter formats. Use when the task requires absorbing the user's source library and adapting it for US/European audiences.
---

# Market Psychology Western Writing

## Purpose

Use the user's source library as research material. Extract mechanisms, cases, and decisions; then rewrite them for Western readers without translating Chinese forum language literally.

## Source boundary

- Read from `knowledge/market-psychology/manifest.json` and `knowledge/market-psychology/chanlun/manifest.json`.
- Treat extracted text as source material, not verified current facts.
- Preserve source attribution, uncertainty, dates, and contradictions.
- Never present an old market prediction as a current forecast without fresh verification.
- Do not provide personalized investment advice or guaranteed returns.

## Required transformation

1. Identify the source's central event, claim, and emotional conflict.
2. Separate observation, interpretation, prediction, and hindsight.
3. Extract the investor psychology: loss aversion, FOMO, regret, overconfidence, confirmation bias, panic selling, revenge trading, leverage, forced liquidation, and inability to accept being wrong.
4. Map Chinese context to a familiar Western investor situation: earnings, Fed decisions, rate cuts, inflation, options, margin calls, index funds, crypto cycles, or a single-stock thesis. Do not invent facts; mark analogies as analogies.
5. Build a concrete human story before stating the lesson.
6. Write natural American English. Prefer short sentences, active verbs, specific images, and spoken rhythm.
7. Remove literal translations, Chinese internet slang, grand predictions, moralizing, and unsupported certainty.
8. End with a psychological insight or decision question, not a stock pick.

## Output modes

- X short post: 40–90 words, one emotional turn, one insight.
- X thread: 5–9 posts, hook, setup, escalation, reversal, lesson.
- Video narration: 30–90 seconds, spoken English, scene beats, pause points.
- Investor essay: 600–1,200 words with source note and uncertainty labels.
- Bilingual research card: Chinese mechanism, English adaptation, audience trigger, evidence status.

## Quality gate

Before delivery, check:

- Is the first line understandable to a Western investor?
- Is there a person making a decision?
- Is the emotional mechanism visible through behavior?
- Is the market context concrete but not fabricated?
- Are old claims clearly dated?
- Does the English sound native rather than translated?
- Does the ending change how the reader sees the decision?
- Is there any hidden stock recommendation or promise?

## Companion skills

Use with:
- `.agents/skills/story-script-master` for causal story structure and pacing.
- Marketing psychology skills for audience response and mental models.
- An English style or humanizer skill for final prose review.

## Evidence labels

Mark internal work as:
- SOURCE: directly present in the uploaded material.
- ADAPTATION: cultural translation for Western readers.
- ANALOGY: explanatory comparison, not source fact.
- CURRENT-CHECK: requires fresh web verification.
- DRAFT: not user-approved for publication.
