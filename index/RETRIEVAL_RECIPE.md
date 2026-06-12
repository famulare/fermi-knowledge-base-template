# Retrieval Recipe (v1.0)

**Contract:** This file defines the exact retrieval procedure Fermi follows
for every substantive query. Deviations must be justified in the response.

---

## Procedure

### Step 1: Consult the router (already loaded at session start)

`index/router.md` provides:
- Domain groupings with file inventories
- Large file section inventories with line ranges
- Recent activity summary

### Step 2: Identify candidate files from the router

- From the query terms, identify 1-3 relevant domain groups
- Within those groups, select 3-8 candidate files most likely to contain the answer
- For ambiguous queries, prefer meta/ files first (pre-synthesized)
- For provenance/exact-quote queries, prefer raw/ files
- For uncategorized files, use the directory breakdown to scope the search

### Step 3: Targeted search within candidates

Search with specific terms **scoped to candidate paths only** (not whole-repo):

```
Grep(pattern="<query terms>", path="meta/models/")
Grep(pattern="<query terms>", path="<specific-file.md>")
```

- For multi-word concepts, search the most distinctive term first
- If no hits in initial candidates, expand to adjacent domains

**Using the search CLI for broader queries:**
```bash
uv run scripts/kb_search.py search "<query terms>"
uv run scripts/kb_search.py search "<query terms>" --layer meta   # synthesis
uv run scripts/kb_search.py search "<query terms>" --layer raw    # provenance
```

### Step 4: Read matching sections (not full files)

- Read the top 3-5 matching files/sections
- **Files under 20KB:** read the full file
- **Files over 20KB** (marked LARGE in router):
  1. Consult the section inventory in the router
  2. Identify the relevant section(s) by heading
  3. Read only those sections using `Read` with `offset` and `limit` parameters
  4. **Never** load the entire file into context

**Using the search CLI for chunk-level reading:**
```bash
uv run scripts/kb_search.py read <chunk_id>
```

### Step 5: Assemble answer with citations

- Cite sources as `file_path:line_number`
- Display origin labels for all claims/models cited
- Distinguish evidence vs inference vs interpolation
- If confidence is low, expand the candidate set and repeat from Step 3

---

## Staleness Check

Before relying on search results, verify the DB is current:
```bash
uv run scripts/kb_search.py status
```
If stale files are reported, either rebuild or fall back to Grep for those files:
```bash
uv run scripts/kb_search.py rebuild
```

---

## Anti-patterns

- **DO NOT** grep the entire repo without scoping to candidate paths first
- **DO NOT** read large files (>20KB) without consulting the section inventory
- **DO NOT** answer from memory when KB content exists — always retrieve
- **DO NOT** preload index/tags.md, entities.md, link_graph.md, or glossary.md
  into context unless the router is insufficient for candidate identification
- **DO NOT** load the full corpus into context at session start
