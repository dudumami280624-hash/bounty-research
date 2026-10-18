# Agent entrypoint — bounty-research

Before changing this repository:
1. Read `HANDOFF.md`, `task_plan.md`, `findings.md`, and `progress.md`.
2. For complex tasks use `.agents/skills/planning-with-files/SKILL.md`.
3. For context transfer use `.agents/skills/handoff/SKILL.md`.
4. Verify the real state of `status/audit_status.json` and GitHub Actions; do not assume HANDOFF.md is current.
5. Update planning and progress files after meaningful work. Record the command, result, and remaining blockers.
6. Before ending a work session, update HANDOFF.md with a dated section; never replace its historical contents.
7. Never treat a passing workflow as evidence of a real vulnerability, submitted report, or earned bounty.

The workflow `planning-handoff-gate.yml` automatically validates these files on push, pull requests, and a daily schedule. This is repository automation, **not** proof of interactive Codex hook activation.
