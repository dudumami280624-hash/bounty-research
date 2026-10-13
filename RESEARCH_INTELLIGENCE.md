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

## 6. Five-module discovery upgrade (offline and authorized only)
1. Target intake: record official authorization, cash eligibility, pinned source, permitted test methods, reproducibility, and missing facts. Reject out-of-scope candidates before scoring.
2. Discovery: combine static alerts with privilege/asset flow review, state transitions, patch diff review, and root-cause hypotheses. Record each hypothesis with source lines and an explicit security invariant.
3. Invariant fuzzing: write Foundry unit/invariant tests for asset conservation, authorization boundaries, reward accounting and state consistency. Keep synthetic tests separate from deployment evidence.
4. False-positive triage: classify each lead as open, disproved, blocked, duplicate-public or verified; require reachability, attacker control, measurable impact, known-issue checks and review evidence before promotion. Never bypass duplicate_gate.
5. Evidence and acceptance: store pinned commit, command, environment, logs, reproduction, impact, scope and independent review. Do not count mock tests as real findings or automatically submit reports.

## 7. Operational metrics and release gates
- Target coverage: eligible and independently scope-checked targets / all evaluated targets; count missing authorization as ineligible, not as verified.
- Deep investigation completion: leads with documented reachability, attacker control, impact and disposition / leads opened.
- Reproduction rate: leads with reproducible isolated anomaly / leads fully investigated.
- Confirmed finding rate: genuine in-scope independently supported findings / fully investigated leads.
- False-positive rate: disproved leads / fully investigated leads.
- Public duplicate prevention: confirmed public root-cause duplicates blocked / confirmed public root-cause duplicates encountered.
- Report acceptance: officially accepted reports / officially decided reports.
- Verified bounty yield: confirmed USD payouts / recorded research hours.
All metrics include observation window, provenance, numerator and denominator. A zero denominator yields unknown, not 0% or 100%. CI passing is an engineering metric only; it cannot pass business stage 3.

## 8. Upstream reference adoption (2026-10-13)
Research references (public examples, not new bounty findings):
- crytic/echidna: stateful property fuzzing, corpus guidance, minimization, and machine-readable JSON outcomes; https://github.com/crytic/echidna
- foundry-rs/forge-std: handler-targeted invariant tests and assertions; https://github.com/foundry-rs/forge-std
- crytic/slither: SlithIR-backed detectors, custom analysis and property tooling; https://github.com/crytic/slither
- horsefacts/weth-invariant-testing: minimal handler/invariant learning fixture; https://github.com/horsefacts/weth-invariant-testing
- secureum/DeFi-Security-Summit-Stanford: offline vulnerability regression examples; https://github.com/secureum/DeFi-Security-Summit-Stanford
- code-423n4/2024-01-renft: public historical scope, static findings and known-issue exclusion examples; https://github.com/code-423n4/2024-01-renft

Adaptation order: (1) extract negative/positive invariant fixtures from public examples, preserving attribution and license requirements; (2) measure whether handlers exercise meaningful authorized state transitions, recording revert/discard ratios; (3) add stateful fuzzing with deterministic seed and minimized counterexamples; (4) compare Slither hypotheses to reachable code and known issues; (5) replay independently on pinned authorized source. Never classify public examples as original discoveries. No external dependency is considered integrated until an executable test and CI evidence exist.

## 9. Publicly documented real findings as regression benchmarks
Echidna's official repository https://github.com/crytic/echidna documents historical findings for 0x Protocol, Balancer Core, Liquity Dollar, Origin Dollar and Yield Protocol. These are historical examples, NOT novel bounty findings. Extract property classes: no free pool shares/assets, accounting conservation, valid cancelability, precision bounds, and balance <= supply. For each benchmark: preserve upstream link and license, pin original vulnerable/fixed revisions when available, verify reproducer on vulnerable revision and non-reproduction on fixed revision, then adapt the invariant to a separate officially authorized target. Record coverage and counterexample reduction, not just PASS counts.
Trail of Bits secure workflow reference: https://github.com/trailofbits/skills/blob/main/plugins/building-secure-contracts/skills/secure-workflow-guide/SKILL.md. Require access-control map, token behavior assumptions and state-transition inventory before fuzzing. Avoid production transactions; use isolated local or permitted fork tests only.
