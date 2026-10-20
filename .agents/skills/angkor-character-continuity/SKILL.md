---
name: angkor-character-continuity
description: Preserve approved Angkor film character identities across stills, shots and video while reducing random regeneration.
---

# Angkor Character Continuity — Original Project Skill

## Purpose
Protect LOCKED character identity in 《梦中回到昔日的吴哥》 and reduce repeated Seedance generations. This is a project-original workflow; it does not incorporate third-party skill text.

## Mandatory references
Read `film/angkor/AGENTS.md`, `PROJECT_HANDOVER.md`, `LOCKED_ASSET_REGISTRY.md`, `SCENE_MASTER_LOCKS.md`, and the relevant `characters/<ID>/LOCKED_MASTER.md`. Use `.agents/skills/angkor-film-production/SKILL.md` for actual asset archiving.

## Identity gates
1. Identify the exact character ID and approved LOCKED version; never silently replace or regenerate a master.
2. Retrieve actual original image bytes. Verify registered SHA-256 when possible. If missing, classify `REFERENCE_MISSING` and do not claim the original face is preserved.
3. Record immutable traits only from verified original imagery or approved written locks: facial geometry, age, hairstyle/headwear, costume, build, distinguishing features and props. Do not invent unrecorded traits.
4. Distinguish MASTER (immutable), APPROVED_REFERENCE (derived and user-approved), SHOT_KEYFRAME (draft), and VIDEO_CLIP (draft).
5. For each shot choose the nearest approved reference for angle, lighting and pose. Do not demand radical pose, face rotation, costume and lighting changes in one generation.

## Shot protocol
- Prepare a short continuity card: character ID/version, reference file path/checksum, unchangeable traits, allowed expression/action, camera framing, lighting, scene, props, start/end composition.
- Use image-to-video with a verified approved first frame when available. Add an approved end frame only when the selected model supports it and it helps.
- One principal action and one main camera movement per short shot; break tool interactions into separate coverage if necessary.
- Keep the prompt focused on the permitted movement and environmental changes; don't re-invent the face, clothing or scene.
- Check before paid generation: input image accessible, reference bindings correct, duration/aspect/model supported, shot physically plausible, no contradictory camera commands, backup destination ready.
- If generation fails, record exact drift (face, costume, body, prop, scene, motion). Fix the reference, staging or shot design first; don't blindly regenerate. After repeated same-mode failures, stop and change production approach.
- Video review is frame-by-frame where possible, comparing face, costume, body, props and scene to the approved reference. Only the user may approve a new locked derivative.

## Shot record fields
`shot_id`, `character_id`, `locked_version`, `reference_path`, `reference_sha256`, `scene_id`, `prompt_path`, `model`, `duration`, `generation_attempt`, `drift_category`, `qa_result`, `approval`, `output_path`, `backup_status`, `remote_commit`.
Use null or `NOT_VERIFIED` for unknowns. Never fabricate file hashes or claim missing media has been archived.

## Licensing and tool boundary
Upstream research references: GenielabsOpenSource/style-consistency-ai (PolyForm Noncommercial 1.0.0; do not copy its skill into a commercial pipeline without permission); fal-ai-community/skills character-design (README says MIT; license scope requires verification; genmedia CLI, model-routing and provider credentials for execution). This original skill provides independent instructions only; no third-party code is installed. API costs and video-generation access require explicit user approval.

## Delivery
Provide a Chinese continuity diagnosis, a shot-ready production brief, and verified asset/archive status. Follow project handover requirements. This skill does not itself render video, restore old Library images, or run unattended.
