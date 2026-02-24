# Fermi Quick Reference

Fast lookup for common operations during Fermi sessions.

---

## Ingest Quick Reference

### Chat Save
```
Trigger: "save this conversation" or "ingest"
Workflow: .claude/workflows/INGEST_CHAT.md
Creates: raw/chats/YYYY-MM-DD_topic.md
```

### Markdown Ingest
```
Trigger: Pasted text or "ingest this"
Workflow: .claude/workflows/INGEST_MARKDOWN.md
Creates: raw/notes/YYYY-MM-DD_title.md
```

---

## File Naming Conventions

- **Raw chats:** `raw/chats/YYYY-MM-DD_topic-slug.md`
- **Raw notes:** `raw/notes/YYYY-MM-DD_title-slug.md`
- **Raw files:** `raw/files/YYYY-MM-DD_original-filename.ext`
- **Provenance:** `raw/provenance/YYYY-MM-DD_filename.json`
- **Meta claims:** `meta/claims/YYYY-MM-DD_claim-slug.md`
- **Meta models:** `meta/models/YYYY-MM-DD_model-slug.md`
- **Meta maps:** `meta/maps/domain-name.md` (not dated - living docs)
- **Contradictions:** `meta/contradictions/YYYY-MM-DD_tension-slug.md`
- **Timelines:** `meta/timelines/topic-name.md` (not dated - living docs)

---

## Origin Labels

**Use in all meta entries:**

- `Origin: [UserName]` - Your ideas, statements, positions
- `Origin: Fermi (‹model›)` - Fermi-generated ideas
- `Origin: Co-created ([UserName] + Fermi (‹model›))` - Collaborative synthesis
- `Origin: External (Author Name)` - Someone else's work

**When ambiguous:** Default to Co-created with explanation

---

## Index Update Checklist

After each ingest, check:

- [ ] **Tags** - Add 1-3 high-signal tags (mechanisms, patterns, domains)
- [ ] **Entities** - Register new named entities with aliases
- [ ] **Links** - Create structurally meaningful links only
- [ ] **Glossary** - Add new definitions if terms introduced

---

## Connection Surfacing Filter

**Surface only if:**
- Cross-domain structural similarity
- Contradiction with prior KB content
- Scale-crossing insight (micro↔macro)
- Non-obvious synthesis opportunity

**Do NOT surface:**
- Topical similarity
- Recency-based associations
- Superficial analogies

---

## Mode Detection

- **Ingest:** "save", "ingest", "add to KB", "remember", pasted text
- **Query:** Questions, "what do we know", "retrieve", "search"
- **Critique:** "critique", "red-team", "what's wrong with"
- **Synthesis:** "synthesize", "consolidate", "reconcile"

If ambiguous: Ask ONE clarifying question

---

## Common Commands

- `/goodbye-kb` - Session checkpoint (commits and pushes)
- Read FERMI.md at session start
- Check `.claude/workflows/` for detailed procedures
- Use templates in `meta/*/_template.md`

---

## Epistemic Discipline Reminders

1. **Evidence ≠ Inference** - Distinguish clearly
2. **Assumptions explicit** - Never hide them
3. **Uncertainty flagged** - Say "I don't know" with explanation
4. **Backlinks required** - Meta must trace to raw
5. **Origin labels mandatory** - On all non-trivial ideas
6. **High-signal tags only** - Prefer 20-50 tags total
7. **Non-trivial connections** - Filter for explanatory value
