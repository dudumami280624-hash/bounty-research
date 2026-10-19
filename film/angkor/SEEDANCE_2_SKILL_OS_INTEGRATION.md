# Angkor Film — Seedance 2.0 Skill OS integration

Upstream: https://github.com/Emily2040/seedance-2.0 (v6.7.0 at integration review, MIT). This is a project integration guide, NOT an installation of the upstream skill into ChatGPT's runtime. Read the upstream SKILL.md and references before generating production prompts.

## Source of truth
- Character and prop identity: `film/angkor/LOCKED_ASSET_REGISTRY.md` and original PNGs in ChatGPT Library, not GitHub.
- Other approved locked characters: DARA V1.0 and KING_SURYAVARMAN_II V3.0 in /Angkor_Film/Characters/; verify before use.
- Never redesign a locked face, headdress, clothing, age, or approved tool.
- Crops and collages are not independently rendered clean video-ready character sheets.

## Per-shot workflow
1. Analyze the user's existing video, mark timecode, continuity, story function and specific defect.
2. Select exactly the locked character master(s) relevant to the shot. Upload actual references to the generation provider; textual asset names alone do not bind identity.
3. Apply upstream Skill OS shot table: camera geometry, blocking, eyelines, one principal action per shot, physical prop interaction, lighting, last frame and sound.
4. Produce concise Chinese Seedance 2.0 prompt with explicit @ reference bindings that match the user's actual UI; do not assume names or slots.
5. Generate short shot, then QA facial identity, headdress, costume, hands, hammer-to-chisel contact, stone debris, background architecture and scene continuity.
6. If failed, revise only the failed shot; keep the original clip and masters immutable.
7. Composite Khmer title as exact UTF-8 text in editing software, not image/video generative text.

## Planned closing sequence
Ancient mason finishes a relief -> match cut to same weathered carving in modern Angkor -> DARA recognizes the connection -> Angkor Wat wide closing shot. This is a proposal, not an approved final edit.

## Acceptance gate
No generated clip is marked approved until reference inputs, prompt, output, and visual review evidence are recorded. Skill OS guides prompts; Seedance provider generates video and may incur costs. No direct provider account integration or unattended rendering is claimed.
