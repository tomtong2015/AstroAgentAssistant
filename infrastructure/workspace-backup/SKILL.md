---
name: workspace-backup
description: Back up the REANA workspace (data, code, figures, chat/agent state, skills) to a downloadable tar.gz — recipes and results, never venv binaries. Restore = untar; skill venvs re-provision themselves.
version: 1.0.0
author: Hermes / AIP
license: MIT
metadata:
  hermes:
    tags: [backup, workspace, archive, restore, reana]
    category: astronomy
---

# Workspace Backup — recipes + data, never binaries

## When to Use
When the user asks to back up / snapshot / export their workspace, or before a
risky operation (workflow re-create, major cleanup, image migration). The
workspace (`$REANA_WORKSPACE`) is persistent NFS, but it is destroyed if the
REANA *workflow* is deleted — a backup archive is the insurance.

## Principles
- **Back up recipes and results, never rebuildable binaries.** Skill venvs
  (`.hermes/envs/`) are caches — they re-provision automatically from each
  skill's `prerequisites.python`. Excluding them keeps archives small and
  portable across image updates.
- Chat history, memory, skills, and config live in `.hermes/` — include them.
- Check the size FIRST; tell the user what you're archiving and how big.

## Backup recipe
```bash
cd "$REANA_WORKSPACE"
du -sh . .hermes 2>/dev/null                       # size check — report this
mkdir -p backups
STAMP=$(date +%Y%m%d-%H%M%S)
tar -czf "backups/workspace-$STAMP.tar.gz" \
    --exclude='./backups' \
    --exclude='./.hermes/envs' \
    --exclude='./.hermes/logs' \
    --exclude='*/__pycache__' \
    --exclude='./.hermes/webui/media_cache' \
    .
ls -lh "backups/workspace-$STAMP.tar.gz"
```
Report the final archive path + size. If the workspace holds multi-GB data
files, ask the user whether to include raw data or archive only code +
`.hermes` (add `--exclude` for the heavy dirs they name).

## How the user downloads it
1. **JupyterLab file browser** (the session's Lab tab): right-click
   `backups/workspace-<stamp>.tar.gz` → Download.
2. **From their laptop:** `reana-client download backups/workspace-<stamp>.tar.gz -w <workflow>`
   (needs their REANA token; workflow name shown in DRP-Hub).
S3 upload is planned (per-user secrets contract) but not yet available — do
not attempt to push archives to remote storage.

## Restore recipe (into a fresh or existing workspace)
```bash
cd "$REANA_WORKSPACE"
tar -xzf backups/workspace-<stamp>.tar.gz          # or the re-uploaded archive
```
- Config/SOUL/skills restore as files immediately (restart the Hermes tile or
  start a new chat to pick them up).
- Per-skill venvs are NOT in the archive by design: each rebuilds on the next
  `skill_manage(edit)` of that skill (any no-op edit triggers provisioning
  from `prerequisites.python`). Tell the user the first use of an affected
  skill will pay a one-time environment rebuild (~1–5 min).

## Cleanup
Keep at most the 3 newest archives unless the user says otherwise:
```bash
cd "$REANA_WORKSPACE/backups" && ls -1t workspace-*.tar.gz | tail -n +4 | xargs -r rm --
```
