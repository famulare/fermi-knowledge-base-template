---
name: goodbye-kb
description: "KB session checkpoint — reviews learning, summarizes KB state, commits and pushes changes. Run at end of every session."
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

2. Review the output. If there are uncommitted KB changes, the script will stage and commit them automatically.

3. If the script reports "No KB changes to commit," confirm the session is clean and say goodbye.

4. Consider whether any learning updates are warranted (the script will prompt for this). Only update learning artifacts if new patterns emerged — it's fine if none did.
