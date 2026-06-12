# Scripts

---

## KB Infrastructure Scripts

These scripts are part of the retrieval-gated architecture. Run with `uv run`.

- **`generate_router.py`** — Generate `index/router.md` from the markdown corpus.
  Walks all content files, groups by domain (using tags), creates section inventories
  for large files. Run after any ingest or structural change.
  ```bash
  uv run scripts/generate_router.py           # Router only
  uv run scripts/generate_router.py --full    # Also validate tags.md + entities.md
  ```
  The `--full` flag validates file references in `index/tags.md` and `index/entities.md`
  against the current corpus, removes stale references, and reports untagged meta files.

- **`kb_search.py`** — Full-text search CLI for the knowledge base.
  Uses SQLite FTS5 with porter stemming. Database: `index/kb_index.db` (gitignored,
  fully rebuildable from markdown).
  ```bash
  uv run scripts/kb_search.py rebuild                  # Full rebuild
  uv run scripts/kb_search.py rebuild --incremental    # Only re-index changed files
  uv run scripts/kb_search.py search "dose response model"
  uv run scripts/kb_search.py search "query" --layer meta --top 5
  uv run scripts/kb_search.py read 42                  # Read chunk by ID
  uv run scripts/kb_search.py status                   # DB stats + staleness
  ```

- **`kb_audit.py`** — Structural validation and accuracy audit for the knowledge base.
  Checks cross-references, origin attribution, status-evidence consistency, and URL/DOI
  patterns across the corpus.
  ```bash
  uv run scripts/kb_audit.py                     # Full audit, human-readable summary
  uv run scripts/kb_audit.py --json              # Machine-parseable JSON output
  uv run scripts/kb_audit.py --severity ERROR    # Filter to ERROR only
  uv run scripts/kb_audit.py --save              # Save results to audit_results/
  ```

- **`kb_maintenance.sh`** — One-shot maintenance runner. Executes router regeneration,
  incremental search rebuild, a post-rebuild stale-file check, and an ERROR-severity
  audit in sequence. Exits non-zero if any step fails or if the search index still
  reports stale files after rebuild. Use between sessions or before a push.
  ```bash
  bash scripts/kb_maintenance.sh
  ```

---

## Session Checkpoint

The `/goodbye-kb` Claude Code skill (`.claude/skills/goodbye-kb/`) orchestrates
end-of-session maintenance:

1. Reviews KB changes this session
2. Regenerates `index/router.md` via `generate_router.py`
3. Refreshes the search index via `kb_search.py rebuild --incremental`
4. **Verifies no stale files remain** after rebuild (loud warning if drift persists)
5. Runs `kb_audit.py --severity ERROR` to catch structural problems
6. Stages, commits, and pushes KB changes

The post-rebuild stale check is the drift tripwire: if incremental rebuild leaves any
file out-of-sync (e.g., mtime skew, script bug, interrupted run), the checkpoint
surfaces it rather than committing silently against a stale index.
