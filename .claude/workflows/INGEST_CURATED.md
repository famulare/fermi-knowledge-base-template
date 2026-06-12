# Workflow: Curated External Content Ingest

**Trigger:** User wants to ingest content created by others (not [UserName]'s work)

**Status:** Implemented 2026-01-24

---

## Purpose

Capture **external content** that [UserName] finds valuable while:
1. Maintaining clear epistemic boundaries (not [UserName]'s thinking)
2. Recording why it's being ingested (REQUIRED)
3. Preserving proper attribution to original creators

**Key distinction from other ingest workflows:**
- `INGEST_WEB` / `INGEST_REPO` are for [UserName]'s content or interpretive extraction
- `INGEST_CURATED` is for external content that should remain clearly attributed to others

---

## When to Use This Workflow

Use INGEST_CURATED when:
- [UserName] finds a paper by someone else that's interesting
- [UserName] encounters a blog post with ideas worth preserving
- [UserName] wants to reference an external repository's architecture
- [UserName] sees AI-generated content from others worth capturing
- Content is clearly **not [UserName]'s work** but valuable for the KB

Use other workflows when:
- Content is [UserName]'s own work → `INGEST_WEB`, `INGEST_REPO`, etc.
- [UserName] is co-author → Use appropriate workflow with [UserName] attribution
- Pure interpretation/synthesis by Fermi → Origin: Fermi

---

## Process Steps

### Step 1: Identify Source and Author(s)

**Determine who created this:**
```
Author type assessment:

1. Single human author
   → Origin: External (Author Name)
   Example: External (Scott Alexander)

2. Multiple human authors
   → Origin: External (First Author et al.)
   Example: External (Smith et al.)

3. Human with AI assistance
   → Origin: External (Author + AI)
   Example: External (Jones + ‹model›)

4. AI-generated content
   → Origin: External (Company Model)
   Example: External (Anthropic Claude ‹model›)
   Example: External ([Provider] ‹model›)

5. Organization/Institution
   → Origin: External (Organization)
   Example: External (WHO)
```

**Gather provenance information:**
- Original URL/source
- Publication date (if known)
- Author affiliations (if relevant)
- Context of creation

---

### Step 2: Ask Why (REQUIRED)

**This step is mandatory.** Unlike other ingest workflows where "why" is optional, curated content MUST have an ingest reason documented.

**Ask user:**
```
Why are you ingesting this external content?

1. **Reference** - Want to cite/reference this in future thinking
2. **Contrast** - Contains ideas that differ from my own thinking
3. **Building on** - Want to extend or build upon these ideas
4. **Learning** - Contains knowledge I want to internalize
5. **Challenge** - Contains arguments I want to engage with critically
6. **Other** - [Specify]

Please also explain briefly: How does this relate to your existing thinking?
```

**Document the response in raw file:**
```markdown
**Ingest Reason:** [Category: Brief explanation]
**Relation to [UserName]'s thinking:** [How this connects to existing KB content]
```

---

### Step 3: Capture Raw

**File location by content type:**

| Content Type | Location |
|--------------|----------|
| Scientific papers | `raw/curated/papers/YYYY-MM-DD_author_title-slug.md` |
| Blog posts | `raw/curated/posts/YYYY-MM-DD_author_title-slug.md` |
| Repositories | `raw/curated/repos/YYYY-MM-DD_owner_repo-name.md` |
| AI artifacts | `raw/curated/artifacts/YYYY-MM-DD_model_description-slug.md` |
| Other | `raw/curated/other/YYYY-MM-DD_title-slug.md` |

**Required header in all raw files:**
```markdown
# [Content Type]: [Title]

**Origin:** External ([Author])
**Original Author(s):** [Full names, affiliations if known]
**Original Source:** [URL or publication info]
**Ingest Reason:** [Why [UserName] found this interesting]
**Ingest Date:** YYYY-MM-DD

---

## Content

[Extracted or summarized content]

---

## Provenance

**Original publication date:** [If known]
**Retrieved from:** [URL]
**Retrieved on:** YYYY-MM-DD
**Extraction method:** [WebFetch | Manual copy | PDF extraction | etc.]
```

---

### Step 4: Extract Meta (Optional - Ask First)

**Unlike other ingest workflows, meta extraction is NOT automatic.**

**Ask user:**
```
Do you want to create meta entries (claims, models, maps) from this content?

1. **Yes** - I want to engage with and structure these ideas
   → Create meta entries with Origin: External (Author)
   → Clear separation from [UserName]'s own claims/models

2. **No** - Keep as reference only
   → Raw capture is sufficient
   → Can create meta entries later if needed

3. **Partial** - Only extract specific items
   → Specify which claims/models to extract
```

**If extracting meta entries:**

All meta entries MUST include:
```markdown
**Origin:** External (Author Name)
**Original Author(s):** [Names]
**Original Source:** [URL/publication]
**Ingest Reason:** [Why ingested]
**Ingest Date:** YYYY-MM-DD
```

Use appropriate templates:
- `meta/claims/_TEMPLATE.md` for claims
- `meta/models/_TEMPLATE.md` for models
- `meta/maps/_TEMPLATE.md` for conceptual maps

---

### Step 5: Connect

**Run CONNECTIONS workflow** to identify relationships between:
- External content and [UserName]'s existing thinking
- External content and other curated material
- External content and KB models/claims

**Connection types to identify:**

| Relationship | Meaning |
|--------------|---------|
| `relates to` | Topically similar, shares subject matter |
| `supports` | External content provides evidence for [UserName]'s ideas |
| `contradicts` | External content conflicts with [UserName]'s ideas |
| `extends` | External content builds on similar foundations |
| `challenges` | External content presents alternative framing |

**Document connections in raw file:**
```markdown
## Connections to KB

**Relates to:**
- `meta/models/YYYY-MM-DD_model.md` - [How related]

**Supports:**
- `meta/claims/YYYY-MM-DD_claim.md` - [How it supports]

**Contradicts:**
- `meta/models/YYYY-MM-DD_model.md` - [Point of conflict]
```

**If contradiction detected:**
- Create `meta/contradictions/` entry
- Link both positions
- Note that one is External origin

---

## Origin Attribution Decision Tree

```
Who created this content?
│
├─ [UserName] (primary or co-author)
│   └─ DON'T use INGEST_CURATED
│       Use INGEST_WEB or INGEST_REPO instead
│
├─ Someone else (human)
│   └─ Origin: External (Author Name)
│
├─ Human + AI collaboration
│   └─ Origin: External (Author + AI)
│
├─ AI-generated (not [UserName]'s)
│   └─ Origin: External (Company Model)
│
└─ Organization/Institution
    └─ Origin: External (Organization)
```

---

## Template: Curated Paper

```markdown
# Paper: [Title]

**Origin:** External ([First Author] et al.)
**Original Author(s):** [Full author list with affiliations]
**Original Source:** [Journal, DOI, URL]
**Ingest Reason:** [Why [UserName] found this interesting]
**Ingest Date:** YYYY-MM-DD

---

## Summary

[Brief summary of paper's main contribution]

---

## Key Claims

1. **[Claim 1]:** [Statement]
   - Evidence: [How supported]
   - Assumptions: [Underlying assumptions]

2. **[Claim 2]:** [Statement]
   - Evidence: [How supported]
   - Assumptions: [Underlying assumptions]

---

## Methods/Approach

[Brief description of methodology]

---

## Relevance to [UserName]'s Thinking

[Why this was ingested - how it relates to existing KB content]

---

## Connections to KB

**Relates to:**
- [Links to related meta entries]

**Supports/Contradicts:**
- [Links with relationship type]

---

## Provenance

**Citation:** [Full citation]
**Retrieved from:** [URL]
**Retrieved on:** YYYY-MM-DD
**Extraction method:** [WebFetch | PDF | etc.]
```

---

## Template: Curated Blog Post

```markdown
# Blog Post: [Title]

**Origin:** External ([Author])
**Original Author(s):** [Author name, affiliation/platform]
**Original Source:** [URL]
**Ingest Reason:** [Why [UserName] found this interesting]
**Ingest Date:** YYYY-MM-DD

---

## Summary

[Main point of the post]

---

## Key Arguments

1. **[Argument 1]:** [Statement]
   - Support: [How justified]

2. **[Argument 2]:** [Statement]
   - Support: [How justified]

---

## Technical Content

[If applicable: code, data, visualizations]

---

## Relevance to [UserName]'s Thinking

[Why this was ingested - how it relates to existing KB content]

---

## Connections to KB

**Relates to:**
- [Links to related meta entries]

---

## Provenance

**Published:** [Date if known]
**Retrieved from:** [URL]
**Retrieved on:** YYYY-MM-DD
```

---

## Template: Curated Repository

```markdown
# Repository: [owner/repo]

**Origin:** External ([Authors/Maintainers])
**Original Author(s):** [Names from README/LICENSE]
**Original Source:** [GitHub URL]
**Ingest Reason:** [Why [UserName] found this interesting]
**Ingest Date:** YYYY-MM-DD
**Commit:** [SHA at time of ingest]

---

## Summary

[What this repository does, its purpose]

---

## Architecture

[High-level architectural description]

---

## Key Design Decisions

1. **[Decision 1]:** [Description]
   - Rationale: [Why this choice]

2. **[Decision 2]:** [Description]
   - Rationale: [Why this choice]

---

## Relevance to [UserName]'s Thinking

[Why this was ingested - how it relates to existing KB content]

---

## Connections to KB

**Relates to:**
- [Links to related meta entries]

---

## Provenance

**Repository:** [URL]
**Commit:** [SHA]
**Retrieved on:** YYYY-MM-DD
**Examination scope:** [What was examined vs skipped]
```

---

## Template: Curated AI Artifact

```markdown
# AI Artifact: [Brief Description]

**Origin:** External ([Company Model])
**Original Author(s):** AI-generated by [Model name and version]
**Original Source:** [URL or context of generation]
**Ingest Reason:** [Why [UserName] found this interesting]
**Ingest Date:** YYYY-MM-DD

---

## Context

[What prompted this AI output, who generated it, why]

---

## Content

[The AI-generated content]

---

## Notable Aspects

[What makes this interesting or worth preserving]

---

## Relevance to [UserName]'s Thinking

[Why this was ingested - how it relates to existing KB content]

---

## Connections to KB

**Relates to:**
- [Links to related meta entries]

---

## Provenance

**Model:** [e.g., Claude ‹model›, [Provider] ‹model›, etc.]
**Generated by:** [User who prompted, if known]
**Generation date:** [If known]
**Retrieved from:** [URL or description]
**Retrieved on:** YYYY-MM-DD
```

---

## Key Differences from INGEST_WEB

| Aspect | INGEST_WEB | INGEST_CURATED |
|--------|------------|----------------|
| Default assumption | [UserName]'s content or interpretive extraction | External content, not [UserName]'s |
| Origin attribution | [UserName] or Fermi | External (Author) |
| Meta extraction | Default yes | Ask first—may be reference only |
| "Why" question | Optional | **Required** |
| Raw location | `raw/web/` | `raw/curated/` |
| Epistemic framing | [UserName]'s ideas or Fermi's interpretation | Preserving others' ideas with attribution |

---

## Index Updates

**Tags:**
- Add relevant domain/topic tags
- Add `curated` tag for easy filtering
- Avoid over-tagging

**Entities:**
- Register external authors if significant
- Register organizations if institutional content
- Register key concepts introduced

**Link Graph:**
- Add `curated → meta` links if meta entries created
- Add cross-references to related KB content

---

## Git Commit Format

```
Ingest: Curated [type] - [Author] - [Short title]

Added external [paper/post/repo/artifact] from [source].

Raw layer:
- raw/curated/[type]/YYYY-MM-DD_filename.md
- Origin: External ([Author])
- Ingest reason: [Brief why]

Meta layer:
- [If created] meta/[type]/filename.md (Origin: External)

Connections to KB:
- [Relates to/supports/contradicts] [meta entries]

Co-Authored-By: Claude (‹model›) <noreply@anthropic.com>
```

---

## Epistemic Discipline Checklist

Before completing curated content ingest:

**Origin Attribution:**
- [ ] Origin correctly set to External (Author)
- [ ] Original author(s) documented
- [ ] Original source URL/publication recorded

**Ingest Reason (REQUIRED):**
- [ ] Asked user why this is being ingested
- [ ] Documented ingest reason in raw file
- [ ] Documented relation to [UserName]'s thinking

**Raw Layer:**
- [ ] File stored in correct `raw/curated/[type]/` directory
- [ ] All provenance fields complete
- [ ] Content extracted/summarized appropriately

**Meta Layer (if applicable):**
- [ ] Asked user before creating meta entries
- [ ] Meta entries use External origin
- [ ] All External provenance fields included

**Connections:**
- [ ] CONNECTIONS workflow run
- [ ] Relationships to KB content documented
- [ ] Contradictions flagged if detected

**Epistemic Clarity:**
- [ ] Clear this is external content, not [UserName]'s thinking
- [ ] Relationship types explicit (relates to vs supports vs contradicts)
- [ ] No conflation with [UserName]'s own ideas

---

## Integration Points

### With CONNECTIONS.md
After curated ingest:
- Check for non-trivial connections to existing KB content
- Distinguish relationship types (supports, contradicts, extends)
- Surface cross-domain patterns if any

### With CONTRADICTIONS.md
If external content conflicts with [UserName]'s ideas:
- Create contradiction entry
- Note one side is External origin
- Document the tension clearly

### With Other Ingest Workflows
- If content turns out to be [UserName]-authored → switch to INGEST_WEB
- If user wants Fermi's interpretation → create separate Fermi-origin meta entry
- Can reference curated content from [UserName]-origin syntheses

---

## Status

**Status:** Implemented
**Created:** 2026-01-24
**Dependencies:**
- Templates: `meta/claims/_TEMPLATE.md`, `meta/models/_TEMPLATE.md`, `meta/maps/_TEMPLATE.md`
- Workflows: CONNECTIONS.md, CONTRADICTIONS.md
- Directory: `raw/curated/` with subdirectories

---

## Summary

INGEST_CURATED captures external content [UserName] finds valuable while maintaining clear epistemic boundaries. Unlike other ingest workflows, it:
1. **Requires** asking why (ingest reason is mandatory)
2. Uses **External origin** attribution exclusively
3. **Asks before** creating meta entries (not automatic)
4. Stores in dedicated `raw/curated/` directory
5. Maintains clear separation from [UserName]'s own thinking

This workflow ensures [UserName] can curate interesting external content without conflating it with his own ideas.
