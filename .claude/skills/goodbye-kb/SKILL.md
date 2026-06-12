---
name: goodbye-kb
description: "KB session checkpoint — summarizes KB state, regenerates the router, refreshes the search index, runs the integrity audit, and commits changes. Run at end of every session."
disable-model-invocation: true
allowed-tools: Bash, Read, Grep, Glob
---

# KB Session Checkpoint

Run the session checkpoint script to close out a KB session.

## Steps

1. Run the checkpoint script:
   ```
   bash .claude/skills/goodbye-kb/goodbye-kb.sh
   ```
   The script regenerates `index/router.md`, refreshes the search index
   (`scripts/kb_search.py rebuild --incremental`) with a post-rebuild stale-file
   check, runs the ERROR-level integrity audit (`scripts/kb_audit.py`), then stages
   and commits any KB changes.

2. Review the output. If there are uncommitted KB changes, the script will stage and commit them automatically across all content directories (`raw`, `meta`, `index`, `views/persistent`, `special_projects`, `contracts`, `examples`).

3. If the audit reports ERRORs or the search index reports stale files after rebuild, resolve those before treating the session as clean.

4. If the script reports "No KB changes to commit," confirm the session is clean and say goodbye.

5. Pushing to a remote is optional and off by default. To push, run the script with `--push`:
   ```
   bash .claude/skills/goodbye-kb/goodbye-kb.sh --push
   ```
