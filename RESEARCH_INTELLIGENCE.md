# Research intelligence and submission-quality mechanisms

This is a design/operational policy, not evidence of an exploitable bug or of improved bounty yield.

## 1. Target prioritization (no speculative bounty promises)
Record for each target: official scope URL and verified timestamp, source/deployment commit, permitted test method, payout eligibility, public disclosure/known-issue links, source recency, accessible reproducible test environment, and research competition proxy (public disclosures only). Missing facts remain unknown, never zero. Rank only after scope and legality checks. Prefer targets with reproducible local tests and low evidence friction; never equate fewer public reports with fewer private duplicates.

## 2. Root-cause knowledge base
For each lead persist: target ID, pinned source SHA, component/function, trigger preconditions, security invariant, root cause fingerprint, impact, controls, PoC evidence path, public related disclosures, outcome (unreviewed/blocked/disproved/verified), reason, reviewer, timestamp. Reuse historical negative evidence; reopen only on code/scope changes or new evidence. A title or CVE keyword match is not sufficient to declare a duplicate. Public checks cannot detect unpublished private reports.

## 3. Measured quality (denominators mandatory)
- Confirmed finding rate = verified real-world findings / fully investigated leads.
- Public duplicate prevention rate = public root-cause duplicates blocked / confirmed public root-cause duplicates encountered. Report unknown when denominator is zero.
- False-positive rate = disproved leads / fully investigated leads (not all static alerts).
- Submission validity rate = officially accepted submissions / officially decided submissions.
- Official duplicate rate = officially marked duplicate submissions / officially decided submissions.
- Research effort = recorded researcher-hours / accepted reports (unknown without time logs).
- Bounty yield = officially confirmed USD payouts / recorded researcher-hours (unknown until paid).
Track sources, observation period and uncertainty. Never fabricate metrics from simulated tests or zero denominators.

## 4. Fail-closed workflow
official scope -> source pin -> static leads -> reachability and control test -> local isolated finding-specific PoC -> real impact proof -> root-cause duplicate review -> independent challenge -> evidence-backed report draft -> explicit per-report user authorization -> official submission receipt -> official status/payout tracking.
No unauthorized production testing; no automatic submission. Duplicate gate in duplicate_gate.py is a *declaration/evidence-field validator*, not an automated web search or independent reviewer. Review attestations must correspond to real documented checks; do not auto-fill to pass.

## 5. Improvement loop
Compare upstream open-source tools by source, licensing, maintenance and measurable capability. Implement one change at a time, add positive and negative regression fixtures, record Actions run ID and before/after metrics. If no new evidence for a lead after two cycles, mark blocked and switch targets. The primary business gate remains 3/6: real in-scope vulnerability verification.
