# Workflow: Web Content Ingest

**Trigger:** User provides web URL or says "ingest this" with URL context

**Status:** Phase 6+ - Newly Implemented

---

## Purpose

Capture **intellectual content** from web sources:
- Scientific papers (published, preprints)
- Blog posts (personal, technical)
- Technical reports and documentation
- Preprints and working papers
- Other web content

**Focus:** Extract ideas, claims, models, assumptions, and evidence — not exhaustive content archival.

---

## When to Use This Workflow vs INGEST_CURATED

| Content | This Workflow (INGEST_WEB) | INGEST_CURATED |
|---------|---------------------------|----------------|
| [UserName]'s papers/posts | Yes | No |
| External content for Fermi synthesis | Yes | No |
| External content to preserve with clear attribution | No | Yes |
| Content [UserName] finds interesting (not his) | Consider INGEST_CURATED | Yes |

**Rule of thumb:** If [UserName] wants external content clearly labeled as someone else's thinking (not his own, not Fermi's synthesis), use INGEST_CURATED.

---

## Supported Content Types

### Detection Strategy

Content type determined by:
1. **Domain patterns** (journals, preprint servers, blog platforms)
2. **URL structure** (doi.org, arxiv.org, biorxiv.org patterns)
3. **HTML structure** (article tags, schema.org metadata)
4. **User specification** if ambiguous

### Content Categories

- **Scientific papers** - Peer-reviewed publications, preprints, working papers
- **Blog posts** - Technical blogs, research blogs, personal posts
- **Technical reports** - White papers, government reports, institutional docs
- **Documentation** - Project docs, API references, technical guides
- **Generic web** - Fallback for other content

---

## Process Steps

### Step 1: Validate and Prepare

**Parse URL:**
```bash
# Validate URL format
# Supports:
# - https://journals.plos.org/...
# - https://arxiv.org/abs/...
# - https://www.biorxiv.org/content/...
# - https://doi.org/10.1371/...
# - Blog URLs, documentation sites, etc.
```

**Check accessibility:**
```bash
# Test URL access
curl -I "$URL" 2>&1 | head -n 1

# If 403/401: May require authentication
# If 404: URL invalid
# If redirect: Follow to final URL
```

**If inaccessible:**
```
This URL requires authentication or is inaccessible.

Options:
1. Provide the content directly (copy/paste) - use INGEST_MARKDOWN
2. Download as PDF and use INGEST_FILE
3. Check URL and retry

Which approach do you prefer?
```

---

### Step 2: Fetch Content

**Using WebFetch:**
```bash
# Fetch page content
# WebFetch converts HTML to markdown automatically
# Extract: title, authors, abstract/summary, main content, metadata
```

**For DOIs, use canonical resolution:**
```bash
# DOIs redirect to publisher sites
# https://doi.org/10.1371/journal.pbio.2002468
# Resolves to actual journal URL
```

**For preprint servers:**
```bash
# arXiv: https://arxiv.org/abs/XXXX.XXXXX
# bioRxiv: https://www.biorxiv.org/content/...
# medRxiv: https://www.medrxiv.org/content/...
```

---

### Step 3: Detect Content Type

**Detection logic:**

#### Scientific Paper Indicators
- Domain: journals.plos.org, nature.com, science.org, cell.com, etc.
- Domain: arxiv.org, biorxiv.org, medrxiv.org, ssrn.com
- URL contains: /article, /paper, doi.org
- HTML: Contains abstract, authors, affiliations, citations
- Schema.org type: ScholarlyArticle

#### Blog Post Indicators
- Domain: medium.com, substack.com, wordpress.com, blogger.com
- Domain: Personal domains with /blog/ path
- HTML: article tag, post metadata, author byline
- No journal structure (no abstract, methods, etc.)

#### Technical Report Indicators
- Domain: .gov, .org institutional sites
- URL contains: /report, /white-paper, /technical
- Document structure: Executive summary, sections, appendices

#### Documentation Indicators
- Domain: docs.*, readthedocs.io, github.io
- URL structure: /docs/, /api/, /reference/
- HTML: Navigation menus, code examples, API references

**If ambiguous, ask user:**
```
URL: [url]
Title: [detected title]

Content type unclear. What is this?
1. Scientific paper (journal or preprint)
2. Blog post or article
3. Technical report
4. Documentation
5. Other (specify)
```

---

### Step 4: Check Authorship

**Ask for [UserName]-authored content:**
```
Are you an author on this [paper/post/report]?

1. Yes - primary author (Origin: [UserName])
2. Yes - co-author (Origin: [UserName] or Co-created, your preference)
3. No - external content for context (Origin: Fermi (‹model›))

This affects origin attribution in meta entries.
```

**Note:** For [UserName]'s content, we're extracting **his** ideas. For external content, we're extracting ideas **about** the topic for KB context.

---

### Step 5: Check for Previous Ingests

**Search for existing ingests:**
```bash
# Look for previous ingests of same URL
grep -r "$URL" raw/web/ 2>/dev/null

# Also check for same DOI (papers may have multiple URLs)
grep -r "$DOI" raw/web/ 2>/dev/null
```

**If found:**
```
Previously ingested: YYYY-MM-DD
Source: [previous URL]
Raw file: raw/web/[type]/YYYY-MM-DD_[slug].md

Strategy:
1. Re-ingest (create new snapshot + note changes)
2. Use existing ingest
3. Cancel

Which approach?
```

**If re-ingest:**
- Create new snapshot with current date
- Note previous ingest in provenance
- Update meta entries if content changed significantly

---

### Step 6: Extract Content (Type-Specific)

## Scientific Paper Extraction

**Priority sections to extract:**

1. **Metadata**
   - Title, authors, affiliations
   - Journal/venue, publication date
   - DOI, PMID, other identifiers
   - Keywords, subject areas

2. **Abstract/Summary**
   - Full abstract text
   - Key findings summary

3. **Introduction/Background**
   - Research question/motivation
   - Prior work context
   - Gaps addressed

4. **Methods**
   - Study design
   - Data sources
   - Analytical approach
   - Key assumptions

5. **Results**
   - Main findings
   - Statistical significance
   - Figures/tables (note what they show, not full data)

6. **Discussion**
   - Interpretation
   - Limitations acknowledged
   - Implications
   - Future work

7. **Conclusions**
   - Key takeaways
   - Recommendations

**Extraction approach:**
```bash
# Use WebFetch with targeted prompts
WebFetch "$URL" "Extract: title, authors, abstract, and main sections.
For each section, preserve key claims, evidence, assumptions, and
limitations. Focus on intellectual content, not full text reproduction."
```

**Accuracy verification (papers):**
After extraction, before saving:
1. **Author list:** Cross-check extracted author list against DOI/PubMed metadata. Do NOT rely on extraction alone — author lists are a known hallucination/truncation risk.
2. **Key numbers:** Verify that quantitative values (percentages, confidence intervals, p-values, sample sizes) in the extraction match the source exactly. Include inline source annotations: `(source: Table 2 / Equation 5 / p. 12)`.
3. **Provenance consistency:** Ensure the author list in the Provenance section matches the Authors section in the header.

**Grouped extraction checklist (multiple sources in one file):**
When extracting multiple papers, reports, or documents into a single file:
1. **Hard boundaries:** Each source gets its own clearly headed section. No narrative bridges that blur source boundaries.
2. **Per-source attribution:** Every finding, number, and claim must be explicitly tagged to its source within the file. Never let a claim float between sections.
3. **No cross-source inference in body:** Cross-document themes or synthesis belong in a clearly labeled "Cross-Document Themes" section at the end, not woven into individual source sections.
4. **Conflation self-check:** After extraction, review each source section and ask: "Could any claim in this section actually belong to an adjacent source?" Pay special attention to:
   - Country-specific results in multi-country collections
   - Parameter values shared across related models
   - Temporal data in sequential reports (Re estimates, prevalence, coverage)
   - Author lists for papers with overlapping co-author sets
5. **Supersession notes:** When a later source in the group revises an estimate from an earlier source, explicitly note the supersession rather than presenting both numbers without context.

---

## Blog Post Extraction

**Priority content to extract:**

1. **Metadata**
   - Title, author, publication date
   - Blog platform/site
   - Tags/categories if present

2. **Summary**
   - What is the main point?
   - What question does it answer?

3. **Key Claims**
   - Main arguments or findings
   - Evidence provided
   - Examples used

4. **Technical Content**
   - Code examples (preserve if central to point)
   - Diagrams/visualizations (describe)
   - Data/results

5. **Context**
   - Why was this written?
   - What problem does it address?
   - Intended audience

**Extraction approach:**
```bash
WebFetch "$URL" "Extract: main argument, key claims, evidence provided,
technical details if present. Summarize examples. Note any assumptions,
limitations, or open questions mentioned."
```

---

## Technical Report Extraction

**Priority content to extract:**

1. **Metadata**
   - Title, authors, institution
   - Report number, publication date
   - Commissioning organization

2. **Executive Summary**
   - Full summary if available

3. **Problem Statement**
   - What issue is addressed?
   - Scope and objectives

4. **Methods/Approach**
   - Analytical framework
   - Data sources
   - Assumptions

5. **Findings**
   - Main results
   - Evidence base
   - Quantitative outcomes

6. **Recommendations**
   - Policy implications
   - Action items
   - Caveats

**Extraction approach:**
```bash
WebFetch "$URL" "Extract: executive summary, problem statement, methods,
key findings, and recommendations. Preserve claims, evidence, assumptions,
and limitations. Note policy implications."
```

---

## Documentation Extraction

**Priority content to extract:**

1. **Metadata**
   - Project name, version
   - Documentation type (guide, API, reference)
   - Last updated date

2. **Purpose**
   - What does this document?
   - Intended use cases

3. **Key Concepts**
   - Core abstractions
   - Design patterns
   - Architecture overview

4. **Examples**
   - Usage patterns (summarize, don't reproduce fully)
   - Common workflows

5. **Assumptions/Prerequisites**
   - Required knowledge
   - Environment assumptions

**Extraction approach:**
```bash
WebFetch "$URL" "Extract: purpose, key concepts, architecture, design
patterns. Summarize usage examples. Note assumptions and prerequisites.
Focus on conceptual understanding, not exhaustive API details."
```

---

## Generic Web Content Extraction

**Fallback extraction:**

1. **Metadata**
   - Title, author/source, date
   - URL, site context

2. **Summary**
   - Main point or thesis
   - Key information

3. **Structure**
   - How is content organized?
   - What sections exist?

4. **Claims**
   - Explicit statements
   - Implicit assumptions

5. **Context**
   - Why would this be in KB?
   - What does it connect to?

---

### Step 7: Store in Raw Layer

**File naming:**

Scientific papers:
```
raw/web/papers/YYYY-MM-DD_first-author_title-slug.md
```

Blog posts:
```
raw/web/posts/YYYY-MM-DD_title-slug.md
```

Technical reports:
```
raw/web/reports/YYYY-MM-DD_institution_title-slug.md
```

Documentation:
```
raw/web/docs/YYYY-MM-DD_project-name_title-slug.md
```

Generic:
```
raw/web/misc/YYYY-MM-DD_title-slug.md
```

**Slug generation:**
- Lowercase, hyphens for spaces
- Remove special characters
- Truncate to ~50 chars
- Example: `polio-eradication-endgame-dynamics`

---

## Template: Scientific Paper

```markdown
# Paper: [Title]

**URL:** [original URL]
**DOI:** [if available]
**Journal/Venue:** [Journal Name] (or preprint server)
**Publication Date:** YYYY-MM-DD
**Ingest Date:** YYYY-MM-DD
**Type:** [Research Article | Review | Preprint | Working Paper]

**Authors:**
- [First Author] (affiliation)
- [Second Author] (affiliation)
- ...

**Keywords:** [if available]

---

## Abstract

[Full abstract text]

---

## Research Question and Motivation

**Central question:**
[What problem does this address?]

**Motivation:**
[Why is this important? What gap does it fill?]

**Prior work context:**
[What existing work does this build on or challenge?]

---

## Methods

**Study design:**
[Experimental, observational, computational, theoretical, etc.]

**Data sources:**
[Where does data come from? Sample size, timeframe, location?]

**Analytical approach:**
[What methods are used? Models, statistics, algorithms?]

**Key assumptions:**
1. [Assumption 1]
2. [Assumption 2]
...

---

## Main Findings

**Finding 1:** [Statement]
- Evidence: [What supports this?]
- Significance: [Statistical or practical significance]

**Finding 2:** [Statement]
- Evidence: [What supports this?]
- Significance: [Statistical or practical significance]

[Continue for major findings]

**Figures and tables:**
- Figure 1: [Brief description of what it shows]
- Table 1: [Brief description]
[Note: Don't reproduce full data, just document what's shown]

---

## Discussion and Interpretation

**Interpretation:**
[How do authors interpret findings?]

**Comparison to prior work:**
[How do results compare to existing literature?]

**Implications:**
[What does this mean for theory, practice, policy?]

---

## Limitations Acknowledged

1. [Limitation 1] - [Why it matters]
2. [Limitation 2] - [Why it matters]
...

**Not mentioned but evident:**
[Any limitations not explicitly discussed but apparent from methods/scope]

---

## Conclusions

**Key takeaways:**
1. [Takeaway 1]
2. [Takeaway 2]
...

**Recommendations:**
[If any - for policy, practice, or future research]

**Future work:**
[What remains to be done?]

---

## Extractable Claims

**Claim 1:** [Falsifiable statement]
- Evidence: [raw/web/papers/this-file.md:section]
- Assumptions: [What must be true for claim to hold]
- Origin: [[UserName] | Fermi]

**Claim 2:** [Falsifiable statement]
- Evidence: [raw/web/papers/this-file.md:section]
- Assumptions: [What must be true for claim to hold]
- Origin: [[UserName] | Fermi]

[List major claims that should become meta/claims/ entries]

---

## Extractable Models

**Model 1:** [Name/description]
- Core mechanism: [How does it work?]
- Predictions: [What does it predict?]
- Scope: [Where applicable?]
- Origin: [[UserName] | Fermi]

[List conceptual or mathematical models that should become meta/models/ entries]

---

## Uncertainties and Open Questions

**Unresolved:**
1. [What remains uncertain?]
2. [What couldn't be tested?]

**Follow-up questions:**
1. [What should be investigated next?]
2. [What would resolve key uncertainties?]

---

## Connections

**Builds on:**
- [Citation 1] - [How used?]
- [Citation 2] - [How used?]

**Related to other KB content:**
- [meta/models/YYYY-MM-DD_other-model.md] - [How connected?]
- [raw/web/papers/YYYY-MM-DD_other-paper.md] - [How related?]

---

## Raw Evidence Notes

[Any additional quotes, observations, or evidence that doesn't fit above categories but should be preserved]

---

## Provenance

**Authorship:** [[UserName] as [primary author | co-author | not author]]

**Citation:**
[Author list]. ([Year]). [Title]. [Journal]. DOI: [DOI]

**Ingest method:** WebFetch from [URL]

**Related work:**
[If this is part of a series, project, or line of research, note connections]
```

---

## Template: Blog Post

```markdown
# Blog Post: [Title]

**URL:** [original URL]
**Author:** [Author name]
**Publication Date:** YYYY-MM-DD
**Ingest Date:** YYYY-MM-DD
**Platform:** [Medium | Personal blog | Substack | etc.]

**Tags/Categories:** [if available]

---

## Summary

**Main point:**
[What is the central message or argument?]

**Key question:**
[What question does this answer or explore?]

**Target audience:**
[Who is this written for? Technical level?]

---

## Content

### Introduction/Context

[What problem or situation is being addressed?]

### Main Argument/Content

[Break down main sections or arguments]

**Section 1:** [Heading]
- Key point: [What's being claimed?]
- Evidence/example: [How is it supported?]

**Section 2:** [Heading]
- Key point: [What's being claimed?]
- Evidence/example: [How is it supported?]

[Continue for major sections]

---

## Technical Details

[If applicable: code examples, algorithms, data, visualizations]

**Code/examples:**
[Summarize - don't reproduce everything, but capture key patterns]

**Data/results:**
[If empirical claims are made, what evidence is provided?]

---

## Claims and Arguments

**Claim 1:** [Statement]
- Support: [How is this justified?]
- Strength: [Strong evidence | Anecdotal | Opinion]

**Claim 2:** [Statement]
- Support: [How is this justified?]
- Strength: [Strong evidence | Anecdotal | Opinion]

---

## Assumptions and Limitations

**Assumptions:**
1. [What is taken for granted?]
2. [What context is assumed?]

**Limitations:**
[What caveats or limitations are noted?]

---

## Connections

**Related to:**
- [Other KB content this connects to]
- [References cited or ideas built upon]

**Implications:**
[What does this mean for broader understanding?]

---

## Raw Evidence Notes

[Quotes, examples, or observations worth preserving]

---

## Provenance

**Authorship:** [[UserName] | External author (consider INGEST_CURATED for external)]

**Citation:**
[Author]. ([Date]). [Title]. [Blog name]. [URL]

**Context:**
[Why was this ingested? Part of a series? Response to something?]
```

---

## Template: Technical Report

```markdown
# Technical Report: [Title]

**URL:** [original URL]
**Report Number:** [if available]
**Institution:** [Issuing organization]
**Authors:** [Author list]
**Publication Date:** YYYY-MM-DD
**Ingest Date:** YYYY-MM-DD

**Commissioning Organization:** [If different from institution]

---

## Executive Summary

[Full executive summary if available, otherwise extract key points]

---

## Problem Statement

**Issue addressed:**
[What problem or question is this about?]

**Scope:**
[What is covered? What is excluded?]

**Objectives:**
[What does the report aim to accomplish?]

---

## Background and Context

[Situational context, prior work, why this was commissioned]

---

## Methods and Approach

**Framework:**
[Analytical or methodological approach]

**Data sources:**
[What data is used?]

**Assumptions:**
1. [Assumption 1]
2. [Assumption 2]
...

---

## Findings

**Finding 1:** [Statement]
- Evidence: [What supports this?]
- Implications: [What does this mean?]

**Finding 2:** [Statement]
- Evidence: [What supports this?]
- Implications: [What does this mean?]

[Continue for major findings]

---

## Recommendations

**Recommendation 1:** [Action item]
- Rationale: [Why?]
- Implementation: [How?]
- Caveats: [Under what conditions?]

**Recommendation 2:** [Action item]
- Rationale: [Why?]
- Implementation: [How?]
- Caveats: [Under what conditions?]

---

## Limitations and Uncertainties

**Acknowledged limitations:**
1. [Limitation 1]
2. [Limitation 2]

**Uncertainties:**
[What remains uncertain or requires further investigation?]

---

## Policy Implications

[What does this mean for policy, practice, or decision-making?]

---

## Extractable Claims and Models

[List significant claims or models that should become meta entries]

---

## Connections

**Related work:**
[References, prior reports, related analyses]

**Related KB content:**
[Connections to existing meta entries]

---

## Raw Evidence Notes

[Additional quotes, data, or observations]

---

## Provenance

**Authorship:** [[UserName]'s role if any]

**Citation:**
[Author list]. ([Year]). [Title]. [Institution]. [Report number]. [URL]

**Context:**
[Project context, why this was created]
```

---

## Template: Documentation

```markdown
# Documentation: [Project/System Name] - [Doc Title]

**URL:** [original URL]
**Project:** [Project name]
**Version:** [if specified]
**Last Updated:** YYYY-MM-DD (from source)
**Ingest Date:** YYYY-MM-DD

**Documentation Type:** [Getting Started | API Reference | Architecture Guide | Tutorial | etc.]

---

## Purpose

**What is documented:**
[What system, library, or concept?]

**Intended use:**
[Who is this for? What should they learn?]

**Prerequisites:**
[What knowledge or setup is required?]

---

## Key Concepts

**Concept 1:** [Name]
- Definition: [What is it?]
- Purpose: [Why does it exist?]
- Usage: [How is it used?]

**Concept 2:** [Name]
- Definition: [What is it?]
- Purpose: [Why does it exist?]
- Usage: [How is it used?]

[Continue for major concepts]

---

## Architecture/Design

[If applicable: overall system architecture, design patterns, component relationships]

**Components:**
- [Component 1]: [Role and responsibility]
- [Component 2]: [Role and responsibility]

**Design patterns:**
[What patterns are used? Why?]

---

## Usage Patterns

**Common workflow 1:**
[Describe typical usage pattern - summary, not full reproduction]

**Common workflow 2:**
[Describe typical usage pattern - summary, not full reproduction]

---

## Assumptions and Constraints

**Assumptions:**
1. [What is assumed about the environment, user knowledge, etc.?]
2. [What conditions must be met?]

**Constraints:**
[Limitations, requirements, boundaries]

---

## Extractable Patterns

[Design patterns, architectural decisions, or concepts worth capturing as meta entries]

---

## Connections

**Related documentation:**
[Other docs in same project]

**Related KB content:**
[Connections to meta entries]

---

## Raw Evidence Notes

[Specific examples, code patterns, or details worth preserving]

---

## Provenance

**Project:** [Project name and maintainers]

**Authorship:** [[UserName]'s role if any]

**Citation:**
[Project name]. ([Version/Date]). [Doc title]. [URL]
```

---

### Step 8: Generate Meta Entries

**Primary meta type varies by content:**

#### Scientific Papers → Models + Claims
- **Models** if paper presents framework, theory, or mechanism
- **Claims** for empirical findings, predictions, assertions
- Both if paper has conceptual framework + findings

#### Blog Posts → Claims or Maps
- **Claims** if making specific assertions
- **Maps** if providing overview or architectural thinking
- Less likely to produce formal models (but possible)

#### Technical Reports → Claims + possibly Models
- **Claims** for findings and recommendations
- **Models** if analytical framework is generalizable

#### Documentation → Maps (rare)
- Usually doesn't warrant meta entries unless documenting novel patterns
- Exception: If documenting architecture worth capturing as model

---

## Origin Attribution Decision Tree

```
Is this authored by [UserName]?
├─ Yes (primary author)
│   └─ Origin: [UserName]
│       - His ideas, extracted and organized
│       - Meta entries are his claims/models
│
├─ Yes (co-author)
│   └─ Ask: Should these be "Origin: [UserName]" or "Origin: Co-created ([UserName] + Fermi)"?
│       - [UserName]: If his contributions are primary focus
│       - Co-created: If collaborative synthesis
│
└─ No (external author)
    └─ CONSIDER USING INGEST_CURATED WORKFLOW INSTEAD
        │
        ├─ If [UserName] wants to preserve as external content with clear attribution:
        │   └─ Use INGEST_CURATED workflow
        │       - Origin: External (Author Name)
        │       - Stored in raw/curated/
        │       - Requires "why" reason
        │       - Clear epistemic boundary maintained
        │
        └─ If [UserName] wants Fermi's interpretive synthesis:
            └─ Origin: Fermi (‹model›)
                - Interpretation of external work
                - Bringing external ideas into KB for context
                - In Origin detail: cite original authors
```

**When to use INGEST_CURATED vs continuing with INGEST_WEB:**

| Scenario | Workflow | Rationale |
|----------|----------|-----------|
| Paper [UserName] wants to reference | INGEST_CURATED | Keep clear it's external thinking |
| Paper [UserName] wants Fermi to analyze | INGEST_WEB | Fermi's interpretation is the value |
| External blog [UserName] found interesting | INGEST_CURATED | Preserve external attribution |
| External paper for topical context | Either | Depends on whether [UserName] wants clear attribution or synthesis |

**Example origin detail for [UserName]'s paper:**
```markdown
**Origin:** [UserName]

**Origin detail:**
Paper authored by [UserName] et al.
Published: [Journal], [Date]
DOI: [doi]

[UserName] designed the study and analysis; I extracted and structured claims/models
from the published work.
```

**Example origin detail for co-created synthesis:**
```markdown
**Origin:** Co-created ([UserName] + Fermi (‹model›))

**Origin detail:**
Paper authored by [UserName] et al.
Published: [Journal], [Date]
DOI: [doi]

[UserName]'s contribution: Original research and findings
Fermi's contribution: Interpretive synthesis and structural organization
```

**Example origin detail for Fermi's interpretive extraction:**
```markdown
**Origin:** Fermi (‹model›)

**Origin detail:**
This is an interpretive extraction from external research.

Original authors: [Names]
Paper: [Title], [Journal], [Date]
Raw capture: raw/web/papers/[file].md

I extracted claims and models to provide KB context on [topic]. Original
authors stated findings; this is my synthesis for [UserName]'s knowledge base.

Note: For external content with clear attribution preserved, consider using
INGEST_CURATED workflow with Origin: External (Author).
```

---

### Step 9: Run Epistemic Discipline Workflows

After creating meta entries, automatically run:

#### CONTRADICTIONS Workflow
```bash
# Check for tensions with existing content
# Search meta layer for similar topics with conflicting positions

# Example checks:
grep -r "[key concept]" meta/claims/ --include="*.md"
grep -r "[key concept]" meta/models/ --include="*.md"

# Assess if new claims/models conflict with existing ones
# If tension detected, confirm with user before documenting
```

#### CONNECTIONS Workflow
```bash
# Look for non-trivial connections
# Cross-domain patterns, scale-crossing links, shared mechanisms

# Check for:
# - Structural similarity to existing models
# - Assumptions shared across domains
# - Scale-crossing explanations
# - Synthesis opportunities

# Surface only if non-trivial (adds explanatory power)
```

---

### Step 10: Update Indices

**Tags:**
- Add high-signal tags based on content
- Domain tags (epidemiology, vaccine-policy, modeling, etc.)
- Method tags (if applicable)
- Avoid proliferation (prefer 2-4 tags per entry)

**Entities:**
- Authors (if prominent)
- Concepts with aliases
- Projects/systems mentioned
- Organizations

**Glossary:**
- Technical terms requiring precise definition
- Domain-specific vocabulary
- Concepts with multiple meanings

**Link graph:**
- Evidence → claim/model links
- Builds-on relationships
- Related work connections
- Cross-domain patterns if detected

---

### Step 11: Update Views

**Recent Ingests:**
```bash
# Update views/persistent/recent_ingests.md
# Add entry with:
# - Date, title, type
# - Raw location
# - Meta entries created
# - Key claims/models summary
# - Connections surfaced
# - Tags added
```

**Knowledge Map** (`views/persistent/knowledge_map.md`):
(Optional — for narrative overview only; `index/router.md` is the primary navigation surface.)
Update if this ingest opens a new domain area or adds a significant new framework.

**Regenerate Router:**
After updating index files, regenerate the router to reflect changes:
```bash
uv run scripts/generate_router.py
```

---

## Git Commit

**Commit message format:**

```
Ingest: [Content type] - [Author] - [Short title]

Added [paper/post/report/doc] from [source/journal].

Raw layer:
- [raw/web/type/filename.md] - [Content description]
- Provenance: [Authorship, URL, date]

Meta layer:
- [meta/models/filename.md] (Origin: [[UserName]|Fermi]) - [Model description]
- [meta/claims/filename.md] (Origin: [[UserName]|Fermi]) - [Claim description]

Key contributions:
- [Main finding/idea 1]
- [Main finding/idea 2]

Connections surfaced: [If any non-trivial connections]

Contradictions detected: [None | Description if any]

Origin: [[UserName] | External author names]

Co-Authored-By: Claude (‹model›) <noreply@anthropic.com>
```

---

## Special Cases

### Multiple URLs for Same Content

**Example:** DOI + journal URL + PMC URL all point to same paper

**Strategy:**
- Store once with canonical URL (prefer DOI)
- Note alternative URLs in provenance
- Future ingests recognize via DOI/title matching

### Paywalled Content

**If WebFetch fails due to paywall:**
```
This URL is behind a paywall.

Options:
1. Provide PDF - use INGEST_FILE workflow
2. Copy/paste key sections - use INGEST_MARKDOWN workflow
3. Skip for now

Which approach?
```

### Preprint + Published Version

**If same work exists as preprint and published:**
```
This appears to be [preprint version | published version] of work already in KB.

Previous ingest: [date, location]

Strategy:
1. Update existing ingest (note publication status change)
2. Keep both versions (if substantial changes)
3. Skip (use existing)

Which approach?
```

### Series or Connected Work

**If part of blog series or multi-paper project:**
- Note relationship in provenance
- Create timeline entry if showing evolution of ideas
- Consider map entry if architectural overview emerges

---

## Content Type Detection Reference

### Scientific Paper Domains
- journals.plos.org
- nature.com, science.org, cell.com, thelancet.com
- arxiv.org
- biorxiv.org, medrxiv.org
- ssrn.com
- ncbi.nlm.nih.gov/pmc (PubMed Central)
- doi.org (resolves to journal)

### Blog Platforms
- medium.com
- substack.com
- wordpress.com, blogger.com
- Personal domains: /blog/, /posts/, /articles/

### Report Domains
- *.gov (government reports)
- WHO, UN, World Bank institutional sites
- *.edu institutional reports
- Foundation sites ([Institution], Wellcome, etc.)

### Documentation Domains
- *.readthedocs.io
- docs.* subdomains
- github.io (project pages)
- Official project docs

---

## Examples

### Example 1: [UserName]'s PLOS Paper

```bash
URL: https://journals.plos.org/plosbiology/article?id=10.1371/journal.pbio.2002468

# Detect: Scientific paper (PLOS domain)
# Fetch: WebFetch extracts title, authors, abstract, sections
# Ask: "Are you an author?" → Yes (primary)
# Store: raw/web/papers/2017-09-12_[username]_poliovirus-excretion-dynamics.md
# Meta: Create model (excretion dynamics) + claims (duration findings)
# Origin: [UserName]
# Commit: "Ingest: Paper - [UserName] - Poliovirus excretion dynamics"
```

### Example 2: External arXiv Preprint

```bash
URL: https://arxiv.org/abs/2301.12345

# Detect: Preprint (arXiv domain)
# Fetch: WebFetch extracts abstract, sections
# Ask: "Are you an author?" → No
# Store: raw/web/papers/2023-01-15_smith-et-al_neural-network-title.md
# Meta: Create model if novel framework presented
# Origin: Fermi (cite original authors in detail)
# Commit: "Ingest: Preprint - Smith et al - Neural network approach"
```

### Example 3: [UserName]'s Blog Post

```bash
URL: https://[username].com/blog/immunity-modeling-thoughts

# Detect: Blog post (personal domain, /blog/ path)
# Fetch: WebFetch extracts post content
# Ask: "Are you an author?" → Yes
# Store: raw/web/posts/2025-03-20_immunity-modeling-thoughts.md
# Meta: Create claims or map depending on content
# Origin: [UserName]
# Commit: "Ingest: Blog post - [UserName] - Immunity modeling thoughts"
```

---

## Notes on Extraction Depth

**Balance:**
- Preserve key ideas, claims, assumptions, evidence
- Don't reproduce entire papers word-for-word (copyright, bulk)
- Focus on what's needed for KB queries and synthesis
- Raw layer = enough to regenerate understanding
- Meta layer = distilled claims and models

**Rule of thumb:**
- Scientific paper raw: ~20-30% of original length (focused extraction)
- Blog post raw: ~40-50% (more concise sources)
- Technical report raw: ~30-40% (focus on findings/recommendations)
- Documentation raw: ~10-20% (conceptual summary, not full API)

---

## Workflow Status

**Implemented:** YYYY-MM-DD
**Last updated:** YYYY-MM-DD

**Integration:**
- Fully integrated with CONTRADICTIONS and CONNECTIONS workflows
- Follows origin attribution standards (LOCKED)
- Uses raw/web/ storage structure
- Generates appropriate meta entries per content type
