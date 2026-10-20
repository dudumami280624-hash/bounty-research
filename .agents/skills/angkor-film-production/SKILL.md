---
name: angkor-film-production
description: Produce and archive verifiable Angkor film/manju assets across ChatGPT sessions, preserving approved LOCKED masters.
---

# Angkor Film Production & Durable Archive Skill

## Scope and prerequisites
Use for 《梦中回到昔日的吴哥》 under `film/angkor/`. Read repository `AGENTS.md`, `film/angkor/AGENTS.md`, `film/angkor/PROJECT_HANDOVER.md`, `film/angkor/LOCKED_ASSET_REGISTRY.md`, `film/angkor/SCENE_MASTER_LOCKS.md`, and the applicable character lock files before making assets. For multi-step tasks also use `.agents/skills/planning-with-files/SKILL.md` and `.agents/skills/handoff/SKILL.md`.

## Non-negotiable safety
- Never replace, alter, re-label, or regenerate an approved LOCKED master without explicit user approval. Use versioned derivative names, never overwrite.
- Registry records, historical ChatGPT Library IDs, links, or text prompts are not the actual image/video files. If the required locked reference bytes are unavailable, stop dependent image/video generation rather than improvising identity.
- Verify SHA-256 of retrieved locked originals against the registry when provided. Preserve provenance.
- Never upload secrets, private credentials, or material without necessary rights.

## Production workflow
1. **Intake:** Identify requested deliverable (script, storyboard, shot list, prompt, still image, audio, video, subtitles, project file), source references, output format, target folder, and approval/lock status. Do not claim to have an integration with a media generator unless available and tested.
2. **Continuity:** Read locked asset registries, approved scene and character references, and prior shot records. Use `SEEDANCE_2_SKILL_OS_INTEGRATION.md` for shot construction only as a guide, not as an installed Seedance integration.
3. **Create:** Produce the deliverable using actually available tools. For visual assets requiring locked identities, provide actual verified reference images to the generation provider; text labels alone are insufficient. Mark new outputs DRAFT until user approval.
4. **Archive actual bytes:** On user authorization to archive work, upload the original output bytes (not just prompts, thumbnails, metadata, or Library pointers) to a versioned path:
   - `film/angkor/scripts/`, `storyboards/`, `prompts/`, `subtitles/`
   - `film/angkor/assets/characters/`, `assets/scenes/`, `assets/audio/`, `assets/video/`
   - `film/angkor/manifests/` for machine-readable asset inventory.
   Use descriptive stable names with date, asset ID and version. Keep source and derivatives separate.
5. **Verify remote backup:** Read the resulting GitHub file or storage object and confirm size and SHA-256 against local bytes when tools allow. Record commit SHA, location, date, size, checksum, source and approval status. A successful text commit does not establish that media bytes were backed up.
6. **Large files:** GitHub regular Git has practical binary/size limits (warnings over 50 MiB and blocking at 100 MiB); for large media use Git LFS or another durable external object store with user authorization, confirm its binary is retrievable, and record storage location. A Git LFS pointer alone does not prove the binary is available.
7. **Failure handling:** If original bytes cannot be obtained, a binary-upload tool is missing, permission is denied, or verification fails, mark the deliverable `NOT BACKED UP` and explain the blocker and minimum next step. Never imply automatic background syncing.
8. **Handoff:** Add dated verified results, paths and unresolved backups to `film/angkor/PROJECT_HANDOVER.md`; comply with repository-level HANDOFF/progress rules. Preserve prior history. State whether each item is `VERIFIED_BACKUP`, `METADATA_ONLY`, or `MISSING/INACCESSIBLE`.

## Manifest example
```json
{
  "project": "angkor-film",
  "asset_id": "SCENE_004",
  "version": "V1.0_DRAFT",
  "type": "image",
  "path": "film/angkor/assets/scenes/SCENE_004_V1.0_DRAFT.png",
  "storage": "github",
  "bytes": null,
  "sha256": null,
  "commit": null,
  "approval": "DRAFT",
  "backup_status": "NOT_BACKED_UP",
  "verified_at": null
}
```
Do not fill missing fields with fabricated values.

## Session completion checklist
- [ ] Actual deliverable created and accessible
- [ ] LOCKED references preserved and verified where required
- [ ] Actual bytes stored remotely with appropriate permissions
- [ ] Remote file independently read back and checksum/size verified where possible
- [ ] Manifest and handover updated with evidence
- [ ] Any incomplete backups explicitly flagged

## Cross-account recovery
Connect the same GitHub identity with access to this private repository. Read this skill and the handover, then retrieve the **actual committed assets**. Do not confuse access to the repo with access to an old ChatGPT account's Library. This file defines a procedure, not an installed background daemon or guaranteed automatic backup.
