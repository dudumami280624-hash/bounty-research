# Angkor film — assistant operating rules

Scope: `film/angkor/`. These instructions supplement, and do not replace, the repository root `AGENTS.md`. Read root `AGENTS.md`, `HANDOFF.md`, `task_plan.md`, `findings.md`, and `progress.md` as applicable before repository changes.

## Mission
Maintain continuity for the film project 《梦中回到昔日的吴哥》 across ChatGPT accounts and sessions. Treat GitHub as a durable record of verified project decisions, not as a substitute for missing binary assets or account memory.

## Required workflow
1. Inspect actual repository files, relevant commit history, and accessible connected files before claiming a recovery or a completed task.
2. Separate every asset into: **original binary verified**, **metadata/registry only**, or **not found / inaccessible**. Historical Library IDs and paths do not prove present access.
3. Preserve all user-approved LOCKED identities, scene compositions, costumes, props, and versions. Do not overwrite, replace, regenerate, or promote a new master without explicit user approval.
4. To use a locked visual reference, retrieve its actual bytes and verify SHA-256 when available. If inaccessible, stop that dependent visual operation; do not substitute a similar-looking image.
5. Prefer executing authorized work through connected tools. Avoid repeatedly asking for local scans or for facts already in the repository.
6. Respond in clear Chinese. Report verified findings, evidence, changes made, and unresolved blockers. Never claim another ChatGPT account's private files or memories were transferred.
7. Obtain approval before repository writes unless the user has authorized the specific change. Record meaningful changes in a dated handover note and preserve historical content.
8. Do not claim Seedance integration or autonomous rendering is installed; its document is a workflow guide only.

## Project source of truth
- `LOCKED_ASSET_REGISTRY.md`
- `SCENE_MASTER_LOCKS.md`
- `characters/DARA_001/LOCKED_MASTER.md`
- `characters/KING_SURYAVARMAN_II/LOCKED_MASTER.md`
- `SEEDANCE_2_SKILL_OS_INTEGRATION.md`
- `PROJECT_HANDOVER.md` (handover status; validate against live repository)

## Cross-account startup
Read root `AGENTS.md`, this file, `PROJECT_HANDOVER.md`, the locked registries, and recent Git history. Reconnect the same GitHub account with permission for this private repository. Do not infer access to an old ChatGPT account's Library from historical IDs.

## Mandatory durable backup for every new manju / film deliverable
The user's goal is to keep actual creative work recoverable even if ChatGPT account access is lost. For every generated or edited 漫剧/影视 deliverable (scripts, dialogue, storyboards, prompts, shot lists, character/scene designs, images, audio, video, subtitles, project files):
1. **Save the real artifact**, not just a description, ChatGPT Library ID, screenshot, prompt, or URL, into this GitHub repository when the file bytes and GitHub write access are available and the user has authorized the save. Use `film/angkor/` for this project; use clearly named subfolders such as `scripts/`, `storyboards/`, `prompts/`, `assets/characters/`, `assets/scenes/`, `assets/audio/`, `assets/video/`, `subtitles/`, and `manifests/` as appropriate. For other projects, confirm the appropriate folder rather than mixing assets.
2. For each asset, record its relative path, version, date, file size, SHA-256 (when bytes can be hashed), lock/approval status, source and dependencies in a dated manifest or handover record. Preserve originals and version history; never overwrite a LOCKED master or silently replace it.
3. After upload, **verify the remote file actually exists and is readable**, and verify checksum if supported. Report the exact GitHub path/commit. Only then say "backed up to GitHub".
4. For large media or provider/API upload limitations, use Git LFS or another durable storage solution with explicit user authorization and verify the actual binary there; GitHub text pointers, external links, Library IDs, and manifests **alone are not backups**. If bytes cannot be retrieved or transferred, explicitly mark **NOT BACKED UP** and provide the exact blocker. Never claim automatic/background syncing without a real configured and verified workflow.
5. Before ending each creative session, summarize newly generated assets in `PROJECT_HANDOVER.md` and identify any items still not backed up. Follow root-level handoff requirements too. Avoid committing secrets, credentials, or private personal data.
6. If the user asks to generate an asset and saving it is possible, treat backup as part of completion, within available permissions; if the tool cannot write binary outputs to GitHub, do not misrepresent success—ask for the minimum necessary transfer/authorization step.
