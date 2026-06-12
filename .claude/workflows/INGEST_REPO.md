# Workflow: GitHub Repository Ingest

**Trigger:** User provides GitHub repository URL or says "ingest this repository"

**Status:** Phase 6 - Fully Implemented

---

## Purpose

Capture **intellectual content** of codebases:
- Goals and problem space
- Conceptual architecture
- Design assumptions and tradeoffs
- Evident limitations

**NOT exhaustive code indexing** - This is about understanding design intent, not cataloging every function.

---

## When to Use This Workflow vs INGEST_CURATED

| Content | This Workflow (INGEST_REPO) | INGEST_CURATED |
|---------|----------------------------|----------------|
| [UserName]'s repositories | Yes | No |
| External repos for Fermi synthesis | Yes | No |
| External repos to preserve with clear attribution | No | Yes |
| External repos [UserName] finds architecturally interesting | Consider INGEST_CURATED | Yes |

**Rule of thumb:** If [UserName] wants an external repository clearly labeled as someone else's architecture (not his own, not Fermi's synthesis), use INGEST_CURATED.

---

## Supported Repository Types

### Detection Strategy

Repository type determined by:
1. Size (file count, languages)
2. Structure (package files, directory organization)
3. Documentation presence
4. User specification if provided

### Repository Categories

- **Small library** (<100 files) - Full examination possible
- **Medium application** (100-1000 files) - Docs + structure + selective sampling
- **Large framework** (>1000 files) - Documentation-focused
- **Monorepo** - Multiple projects, require scope clarification
- **Documentation repository** - Redirect to markdown ingest
- **Fork** - Ask whether to treat as independent or differential

---

## Process Steps

### Step 1: Validate and Prepare

**Parse repository URL:**
```bash
# Extract owner/repo from URL
# Supports formats:
# - https://github.com/owner/repo
# - https://github.com/owner/repo.git
# - github.com/owner/repo
# - owner/repo (if clearly GitHub format)
```

**Check authentication:**
```bash
# Verify gh CLI is available and authenticated
gh auth status

# Test repository access
gh repo view owner/repo --json nameWithOwner
```

**If authentication fails:**
```
GitHub authentication required.

Please authenticate with: gh auth login

Or provide a public repository URL.
```

---

### Step 2: Gather Repository Metadata

**Get repository information:**
```bash
# Comprehensive metadata
gh repo view owner/repo --json \
  nameWithOwner,description,url,\
  defaultBranchRef,primaryLanguage,languages,\
  createdAt,updatedAt,pushedAt,\
  isArchived,isFork,parent

# Get current commit
gh api repos/owner/repo/commits/HEAD --jq '{
  sha: .sha,
  message: .commit.message,
  author_date: .commit.author.date,
  committer_date: .commit.committer.date
}'

# Get file count and structure
gh api repos/owner/repo --jq '{
  size: .size,
  default_branch: .default_branch
}'
```

**Determine examination strategy based on size:**
```bash
# List root directory
gh api repos/owner/repo/contents --jq '.[] | "\(.type): \(.name)"'

# Estimate repository size
# Small: <100 files visible in structure
# Medium: 100-1000 files
# Large: >1000 files or very large repos
```

---

### Step 3: Define Scope Strategy

**Size-based default strategy:**

#### Small Repository (<100 files)
- Read all documentation
- Examine root structure
- Read entry points (main, lib, index)
- Sample 2-3 core modules
- Document what examined vs skipped

#### Medium Repository (100-1000 files)
- Read all documentation
- Examine full directory structure
- Read entry points
- Infer architecture from organization
- Minimal code sampling
- Explicitly note files not examined

#### Large Repository (>1000 files)
- **Ask user for clarification first:**
```
Repository: owner/repo (estimated >1000 files)

This is a large repository. Recommended approach:
1. Documentation-only (README, architecture docs, no code sampling)
2. Targeted examination (specify modules/components to examine)
3. Cancel

Which approach do you prefer?
```

---

### Step 4: Check for Previous Ingests

**Search for existing ingests:**
```bash
# Look for previous ingests of same repository
grep -l "github.com/owner/repo" raw/repos/*.md 2>/dev/null
```

**If found:**
```
Previously ingested: YYYY-MM-DD (commit: old-sha)
Current commit: new-sha

Strategy:
1. Full re-ingest (new snapshot + conceptual comparison)
2. Cancel (use existing ingest)

Which approach?
```

**If re-ingest selected:**
- Create new snapshot file
- Note previous ingest date and commit in raw file
- In meta layer: Explicitly document what changed conceptually
- Consider timeline entry if major architectural change

---

### Step 5: Examine Repository (Priority Order)

#### Phase 1: Documentation (Always Read)

**Priority order:**
1. **README.md** - Primary source
2. **ARCHITECTURE.md, DESIGN.md** - Design documentation
3. **docs/architecture/**, **docs/design/** - Supplementary docs
4. **CONTRIBUTING.md** - Design philosophy, patterns
5. **LICENSE** - Usage constraints

**Fetch documentation:**
```bash
# Fetch README
gh api repos/owner/repo/contents/README.md --jq '.content' | base64 -d

# Check for architecture docs
gh api repos/owner/repo/contents/ARCHITECTURE.md --jq '.content' | base64 -d 2>/dev/null

# List docs directory
gh api repos/owner/repo/contents/docs --jq '.[] | .name' 2>/dev/null

# Fetch specific docs
gh api repos/owner/repo/contents/docs/architecture.md --jq '.content' | base64 -d
```

#### Phase 2: Structure (Always Examine)

**Get repository organization:**
```bash
# Root directory listing
gh api repos/owner/repo/contents --jq '.[] | "\(.type): \(.name)"'

# Identify project type from key files
# Look for: package.json, setup.py, Cargo.toml, go.mod, pom.xml, etc.

# Get subdirectory structure (selective)
gh api repos/owner/repo/contents/src --jq '.[] | "\(.type): \(.name)"' 2>/dev/null
```

**Infer repository type:**
- Library: Focused API, examples, tests prominent
- Application: Entry points, config, deployment files
- Framework: Extensive abstractions, plugins, extensions
- Tools/CLI: Command definitions, subcommands
- Documentation: Primarily markdown/docs
- Monorepo: Multiple package files, workspaces

#### Phase 3: Code Sampling (Selective)

**Small repositories (<100 files):**
```bash
# Identify entry point
# Common patterns: src/main.*, src/lib.*, src/index.*, cmd/main.go, etc.

# Fetch entry point
gh api repos/owner/repo/contents/src/main.rs --jq '.content' | base64 -d

# Sample 2-3 core modules based on:
# - Imports in entry point
# - README mentions
# - Directory names suggesting core functionality
```

**Medium repositories (100-1000 files):**
- Examine entry point only
- Infer architecture from directory structure
- Note what's NOT examined

**Large repositories (>1000 files):**
- Documentation only (unless user specified targeted examination)

---

### Step 6: Store in Raw Layer

**File naming:** `raw/repos/YYYY-MM-DD_repo-slug.md`

**Slug generation:**
- Format: `owner_repo` (replace `/` with `_`)
- Example: `anthropics_claude-code` from `anthropics/claude-code`

**Template structure:**

```markdown
# Repository: owner/repo

**Repository URL:** https://github.com/owner/repo
**Branch:** main (or default branch name)
**Commit:** [sha] (YYYY-MM-DD HH:MM:SS)
**Ingest date:** YYYY-MM-DD
**Repository type:** [Library|Application|Framework|Tool|Documentation|Monorepo]
**Primary language:** [Language]
**Other languages:** [List]
**Created:** YYYY-MM-DD
**Last updated:** YYYY-MM-DD
**Repository size:** [N] files (estimated)
**Archived:** [Yes/No]
**Fork:** [No | Yes, forked from owner/parent]

## Repository Description

[From GitHub metadata]

---

## Scope of Examination

**Examination strategy:** [Small: full docs + structure + samples | Medium: docs + structure | Large: docs only | Targeted: specific modules]

**What was examined:**
- [x] README.md (full, N lines)
- [x] ARCHITECTURE.md (full, N lines)
- [x] docs/design/*.md (3 files, summarized)
- [x] Root directory structure
- [x] src/main.rs (entry point, N lines)
- [x] src/core/engine.rs (core module, N lines)
- [ ] src/utils/* (12 files, not examined)
- [ ] tests/* (45 files, not examined)

**What was skipped:**
[Explicit list of directories/files not examined]

**Total files examined:** N / M (percentage)

**Rationale:**
Focus on intellectual content: What problem does this solve? How is it architected? What design tradeoffs were made? What assumptions are embedded?

---

## Documentation Capture

### README.md

[Full text or key sections: Overview, Goals, Architecture, Usage]

### ARCHITECTURE.md

[Full text if exists]

### Other Documentation

[Summaries or full text of other key docs]

---

## Repository Structure

### Root Layout

```
owner/repo/
├── src/           [Core implementation]
├── tests/         [Test suite]
├── docs/          [Documentation]
├── examples/      [Example usage]
├── package.json   [Node.js project file]
├── README.md
└── LICENSE
```

### Key Directories

**src/** - [Description of what's here]
**tests/** - [Description]
**docs/** - [Description]

### Key Files

**package.json** - [Project metadata, dependencies, scripts]
**tsconfig.json** - [TypeScript configuration]

---

## Observations

### Goals Stated

[What problems does this repository aim to solve? Extract from README and docs]

Example:
- Enable X by providing Y
- Solve problem Z with approach A
- Alternative to existing tool W because of limitation L

### Architectural Patterns Observed

[High-level architectural structure]

Example:
- Layered architecture: Parser → Analyzer → Renderer
- Plugin system with core + extensions
- Event-driven with message bus
- Monolithic with internal modules

### Design Tradeoffs Noted

[Explicit or implicit tradeoffs in design]

Example:
- Chose simplicity over extensibility (noted in DESIGN.md)
- Performance prioritized over memory efficiency
- Configuration over convention
- Monorepo for easier coordination, harder to split

### Assumptions Evident

[Assumptions embedded in design]

Example:
- Assumes single-threaded execution
- Designed for specific environment (Node.js 18+)
- Expects users to provide configuration
- Built for specific scale (small to medium projects)

### Limitations Acknowledged

[Explicit limitations from docs or evident from design]

Example:
- Not suitable for large-scale deployments (README)
- Limited to specific platform
- Experimental API, subject to change
- Performance degradation at scale

---

## Code Observations

[Only if code was sampled]

### Entry Point Analysis

**File:** src/main.rs

[What entry point reveals about architecture]

Example:
- Initializes 3 main components: Parser, Engine, Renderer
- Uses dependency injection pattern
- Configuration loaded from external file
- Error handling strategy: Result types throughout

### Core Module Analysis

**File:** src/core/engine.rs

[What core module reveals about implementation]

Example:
- State machine with 5 states
- Uses async/await for I/O operations
- Custom error types for specific failure modes
- Extensive use of generics for flexibility

---

## Uncertainties and Omissions

**What remains unclear:**
- [List questions that documentation doesn't answer]
- [Ambiguities in stated design]
- [Gaps in architecture documentation]

**What wasn't examined:**
- [List significant portions not examined]
- [Why they weren't examined]
- [What might be missed as a result]

**Assumptions in this ingest:**
- [Any assumptions made during interpretation]
- [Inferences drawn from limited examination]

---

## Raw Evidence Notes

[Any additional notes, quotes from docs, or observations that don't fit above categories but should be preserved as evidence]

---

[If re-ingest:]
## Previous Ingest

**Previous ingest date:** YYYY-MM-DD
**Previous commit:** [sha]
**Previous ingest file:** raw/repos/YYYY-MM-DD_repo-slug.md

**Conceptual changes since previous ingest:**
- [Major architectural changes]
- [Design philosophy shifts]
- [New capabilities or removed features]
- [Changes in stated goals or scope]

**Stability assessment:**
- Architecture: [Stable | Evolved | Major change]
- Goals: [Unchanged | Refined | Shifted]
- Assumptions: [Same | Modified | Different]
```

**Preservation principle:**
- Capture repository state as evidence
- Preserve what was examined and what wasn't
- Document interpretation boundaries
- Treat as snapshot, not dynamic link

---

### Step 7: Determine Origin Attribution

**Decision tree:**

```
Is this repository authored by [UserName]?
├─ Yes: Ask for attribution preference
│   └─ Present options:
│       1. Origin: [UserName] (his design decisions)
│       2. Origin: Co-created ([UserName] + Fermi (‹model›)) (interpretation of his work)
│       3. Origin: Fermi (treat as external for objectivity)
│       Recommendation: Option 1 if clear authorship
│
└─ No: CONSIDER USING INGEST_CURATED WORKFLOW INSTEAD
    │
    ├─ If [UserName] wants to preserve as external content with clear attribution:
    │   └─ Use INGEST_CURATED workflow
    │       - Origin: External (Repository Authors)
    │       - Stored in raw/curated/repos/
    │       - Requires "why" reason
    │       - Clear epistemic boundary maintained
    │
    └─ If [UserName] wants Fermi's interpretive synthesis:
        └─ Origin: Fermi (‹model›)
            └─ In Origin detail section:
                - Note original repository authors
                - Reference commit and ingest date
                - Clarify this is interpretation
```

**When to use INGEST_CURATED vs continuing with INGEST_REPO:**

| Scenario | Workflow | Rationale |
|----------|----------|-----------|
| External repo [UserName] wants to reference | INGEST_CURATED | Keep clear it's external architecture |
| External repo [UserName] wants Fermi to analyze | INGEST_REPO | Fermi's interpretation is the value |
| External repo architecture to learn from | INGEST_CURATED | Preserve external attribution |
| External repo for pattern comparison | Either | Depends on whether [UserName] wants clear attribution or synthesis |

**For [UserName]'s repository:**
```
Attribution: This repository is authored by you ([UserName]).

How should I attribute the extracted design decisions and architecture?

1. Origin: [UserName] (Recommended)
   - Your design decisions and architectural choices
   - I'm extracting and organizing your existing thinking

2. Origin: Co-created ([UserName] + Fermi (‹model›))
   - I'm interpreting and adding analytical structure

3. Origin: Fermi (‹model›)
   - Treat as external repository for objectivity

Which attribution do you prefer?
```

---

### Step 8: Generate Meta Entries

**Primary meta type: Models** (most common)

Repository ingests typically produce architectural/conceptual models.

#### Architectural Model

**File naming:** `meta/models/YYYY-MM-DD_repo-name-architecture.md`

**Extract:**
- Core architectural pattern (layered, event-driven, plugin-based, etc.)
- Key components and relationships
- Data flow and control flow
- Extension mechanisms
- Explicit design constraints
- Stated tradeoffs
- Scope and scale assumptions

**Use template:** `meta/models/_TEMPLATE.md`

**Origin attribution:**

**For external repositories (Fermi synthesis):**
```markdown
**Origin:** Fermi (‹model›)

**Origin detail:**
This is an interpretive model extracted from repository examination.

Repository: https://github.com/owner/repo (commit: sha)
Raw capture: raw/repos/YYYY-MM-DD_repo-slug.md
Original authors: [Names from README/LICENSE]
Repository created: YYYY-MM-DD
[UserName] ingested: YYYY-MM-DD
Interpretation: Claude (‹model›)

What's interpretation: Architectural patterns, design tradeoffs, and assumptions
inferred from documentation and code structure. Original authors stated goals
and architecture, but this model is my synthesis of that material.

Note: For external repos with clear attribution preserved, consider using
INGEST_CURATED workflow with Origin: External (Authors).
```

**For [UserName]'s repositories:**
```markdown
**Origin:** [UserName]

**Origin detail:**
This repository was created by [UserName].

Repository: https://github.com/[username]/repo (commit: sha)
Raw capture: raw/repos/YYYY-MM-DD_repo-slug.md
Design decisions: [UserName]
Extraction and organization: Claude (‹model›), YYYY-MM-DD

[UserName] designed the architecture; I extracted and structured the description.
```

---

#### Secondary Meta Types

**Claims** - If repository makes specific performance, capability, or design claims

**File naming:** `meta/claims/YYYY-MM-DD_claim-about-system.md`

**Extract:**
- "X is faster than Y by Z%"
- "This approach avoids limitation L"
- "Architecture scales to N users"
- "Design guarantees property P"

**Use template:** `meta/claims/_TEMPLATE.md`

**Origin:** Same as model (Fermi for external, [UserName] for his repos)

---

**Maps** - If repository involves complex domain concepts

**File naming:** `meta/maps/YYYY-MM-DD_repo-domain-map.md`

**Extract:**
- Key concepts and relationships
- Domain terminology
- Conceptual boundaries
- Problem space structure

**Use template:** `meta/maps/_TEMPLATE.md`

---

### Step 9: Create Backlinks

**In all meta entries:**

```markdown
## Evidence Base

Primary source:
- `raw/repos/YYYY-MM-DD_repo-slug.md` - Full repository snapshot
  - README.md section
  - ARCHITECTURE.md section
  - Structure observations
  - Code samples (if applicable)

Repository: https://github.com/owner/repo (commit: sha, ingested YYYY-MM-DD)
```

**For specific documentation references:**
```markdown
- `raw/repos/YYYY-MM-DD_repo-slug.md` (README.md) - [What this shows]
- `raw/repos/YYYY-MM-DD_repo-slug.md` (ARCHITECTURE.md) - [What this shows]
- `raw/repos/YYYY-MM-DD_repo-slug.md` (Structure) - [What this shows]
```

**For code sample references:**
```markdown
- `raw/repos/YYYY-MM-DD_repo-slug.md` (src/main.rs) - [What this shows]
```

---

### Step 10: Update Indices

**Tags** (`index/tags.md`):

Add 1-3 high-signal tags:
- Architecture type: `architecture:layered`, `architecture:event-driven`, `architecture:plugin`
- Domain: `domain:web`, `domain:data`, `domain:cli`, `domain:infrastructure`
- Pattern: `pattern:dependency-injection`, `pattern:state-machine`, `pattern:functional`
- Technology: `tech:typescript`, `tech:rust`, `tech:python`

**Avoid:**
- Generic tags like `code`, `repository`, `github`
- Language tags unless language-specific insight
- Too many tags (prefer 1-3 high-signal)

**Entities** (`index/entities.md`):

Register:
- Repository: `owner/repo`
- Original authors (for external repos)
- Key technologies/frameworks mentioned
- Core concepts if novel to KB

**Format:**
```markdown
## Repositories

- **owner/repo** - [One-line description]
  - Ingested: YYYY-MM-DD (commit: sha)
  - Type: [Library|Application|Framework]
  - Primary language: [Language]
  - Related: [Other repos if applicable]
```

**Glossary** (`index/glossary.md`):

Add domain-specific terms introduced by repository:
- Technical terms defined in docs
- Architecture pattern names
- Domain concepts
- Novel terminology

**Link Graph** (`index/link_graph.md`):

Add structural links:
```markdown
## Repository → Meta

raw/repos/YYYY-MM-DD_repo-slug.md
  → meta/models/YYYY-MM-DD_repo-architecture.md (architectural model)
  → meta/claims/YYYY-MM-DD_performance-claim.md (performance claim)
  → meta/maps/YYYY-MM-DD_domain-map.md (domain concepts)
```

---

### Step 11: Surface Connections

**Check for:**

#### Structural Similarity
Does this architecture resemble existing KB models?
- Similar layering patterns
- Similar component relationships
- Similar tradeoff patterns
- Cross-domain architectural parallels

#### Contradictory Approaches
Does this repository's approach conflict with other KB claims?
- Different solution to same problem
- Contradictory design philosophy
- Tradeoffs prioritized differently

#### Scale-Crossing Insights
Does this implementation illuminate existing abstract models (or vice versa)?
- Abstract pattern now has concrete example
- Implementation details explain why pattern works
- Concrete challenges motivate abstract principles

#### Problem-Solution Patterns
Does this solve a problem encountered elsewhere in KB?
- Novel solution to known problem
- Alternative approach to existing solution
- Addresses limitation of other approach

**Filter criteria:**
- **Must be non-trivial** - Not just "both use TypeScript" or "both are web apps"
- **Must be specific** - Point to specific architectural elements or design choices
- **Must add insight** - Connection should illuminate something about both sides

**Example non-trivial connection:**
```
This repository's three-stage processing (parse → analyze → render) architecturally
similar to KB's two-layer structure (raw → meta → query):
- Both use pipeline architecture
- Both separate preservation from interpretation
- Both face tradeoff: more stages = more flexibility but more complexity

Connection: General pattern of staged processing with fidelity vs flexibility tradeoff
```

**Example trivial connection to AVOID:**
```
This TypeScript repository similar to other TypeScript projects in KB.
[Too generic, no specific insight]
```

---

### Step 12: Check for Contradictions

**If repository contains claims that conflict with existing KB:**

Follow **CONTRADICTIONS.md** workflow:
1. Identify specific tension
2. Document both positions
3. Create contradiction entry
4. Link to both sources

**Example:**
```
Repository X claims "approach A is faster than B"
KB model Y (from repository Z) claims "approach B is faster than A"

→ Create: meta/contradictions/YYYY-MM-DD_approach-a-vs-b-performance.md
```

---

### Step 13: Update Timelines (If Re-ingest)

**If this is a re-ingest with conceptual changes:**

Follow **TIMELINES.md** workflow:

**Create or update:** `meta/timelines/repo-name-evolution.md`

```markdown
# Timeline: owner/repo Evolution

## YYYY-MM-DD (First ingest, commit: sha1)
- Architecture: [Initial architecture]
- Goals: [Initial stated goals]
- Design: [Key design decisions]

## YYYY-MM-DD (Re-ingest, commit: sha2)
- Architecture: [Changed to new architecture]
- Goals: [Refined or shifted]
- Design: [New design decisions]
- **Change:** [Explicit description of what changed conceptually]
```

---

### Step 14: Update Views

**Recent Ingests** (`views/persistent/recent_ingests.md`):

```markdown
### YYYY-MM-DD: owner/repo

**Type:** GitHub Repository ([Library|Application|Framework|Tool])
**Raw location:** raw/repos/YYYY-MM-DD_repo-slug.md
**Repository:** https://github.com/owner/repo (commit: sha)
**Languages:** [Primary], [Others]
**Examination scope:** [Full docs + samples | Docs + structure | Docs only]

**Original authors:** [Names] (for external repos) | [UserName] (for his repos)

**Meta entries:**
  - meta/models/YYYY-MM-DD_repo-architecture.md (Origin: [Fermi|[UserName]])
  - meta/claims/YYYY-MM-DD_performance-claim.md (Origin: [Fermi|[UserName]])

**Key architectural insights:**
[1-2 sentence summary of main architectural patterns extracted]

**Connections surfaced:** [Count if any]
[If re-ingest:] **Re-ingest:** Previous version from [date] (commit: old-sha), conceptual changes documented
```

**Knowledge Map** (`views/persistent/knowledge_map.md`):
(Optional — for narrative overview only; `index/router.md` is the primary navigation surface.)
Update if repository introduces a new domain area or major architectural pattern.

**Regenerate Router:**
After updating index files, regenerate the router to reflect changes:
```bash
uv run scripts/generate_router.py
```

---

### Step 15: Response to User

**Format:**

```
**Repository ingested successfully**

Repository: owner/repo
Commit: [sha] (YYYY-MM-DD)
Languages: [Primary], [Others]

Stored: raw/repos/YYYY-MM-DD_repo-slug.md
Repository: https://github.com/owner/repo

**Examination scope:**
[Summary of what was examined and what was skipped]
- Documentation: README, ARCHITECTURE, [others]
- Structure: Full directory tree
- Code samples: [N files] ([which ones] or [none])
- Files examined: N / M total (X%)

**Transparency:** [Total files not examined], [reasoning]

**Architectural insights extracted:**
[2-3 sentence summary of main architectural patterns, goals, tradeoffs]

**Meta entries created:**
- meta/models/YYYY-MM-DD_repo-architecture.md (Origin: [Fermi|[UserName]])
  [One sentence: Core architectural pattern extracted]

[If claims extracted:]
- meta/claims/YYYY-MM-DD_claim.md (Origin: [Fermi|[UserName]])
  [One sentence: What claim]

**Index updates:**
- Added tags: [tag1], [tag2], [tag3]
- Registered entities: owner/repo, [authors/concepts]
- Added to glossary: [N] terms

[If connections detected:]
**Connections surfaced:**
- [Connection 1 with brief rationale - must be non-trivial]
- [Connection 2 with brief rationale]

[If contradictions detected:]
**Contradictions detected:**
- [Contradiction 1 with brief description]
- Created: meta/contradictions/YYYY-MM-DD_contradiction.md

[If re-ingest:]
**Re-ingest notes:**
- Previous: YYYY-MM-DD (commit: old-sha)
- Changes: [Brief conceptual changes]
- Timeline: [created/updated]

**Citation format:**
`raw/repos/YYYY-MM-DD_repo-slug.md` (full snapshot)
`raw/repos/YYYY-MM-DD_repo-slug.md` (section) for specific docs/code
```

---

## Special Cases

### Case 1: Very Large Repository (>1000 files)

**Detection:**
- File count estimation during structure examination
- Very large repository size from metadata
- Known large frameworks (React, Linux, etc.)

**Action: Ask for clarification**
```
Repository: owner/repo (estimated >1000 files)
Type: [Framework|Large application]
Primary language: [Language]

This is a large repository. Recommended approach:

1. Documentation-only (Recommended)
   - Read all documentation
   - Examine root structure
   - No code sampling
   - Focus on stated architecture and goals

2. Targeted examination
   - Specify modules/components to examine
   - Example: "Focus on parser and core engine"
   - I'll examine docs + specified areas

3. Cancel
   - Use existing documentation or resources instead

Which approach do you prefer?
```

**If documentation-only selected:**
- Follow Phase 1 (docs) and Phase 2 (structure) only
- Skip Phase 3 (code sampling) entirely
- In raw file, explicitly state:
  ```
  Total files examined: N / M (X%)
  Code sampling: None (large repository, documentation-focused)
  ```
- In meta entries, note:
  ```
  **Scope note:** This model is based on documentation and stated architecture.
  Implementation details not examined due to repository size (M files).
  ```

**If targeted selected:**
- Ask for specific modules
- Examine docs + structure + specified areas only
- Document targeted scope clearly

---

### Case 2: Re-ingest (Same Repository)

**Detection:**
```bash
# Search for existing ingests
grep -l "github.com/owner/repo" raw/repos/*.md 2>/dev/null
```

**If found:**
```
Previously ingested: YYYY-MM-DD (commit: old-sha)
Current commit: new-sha ([N] commits ahead)

Strategy:
1. Full re-ingest (Recommended if significant time passed)
   - Create new snapshot
   - Compare architectures
   - Document conceptual changes
   - Consider timeline entry if major evolution

2. Cancel
   - Use existing ingest from [date]

Which approach?
```

**If full re-ingest selected:**

1. **Create new raw file:**
   - File: `raw/repos/YYYY-MM-DD_repo-slug.md` (new date)
   - Include section: "Previous Ingest" with old commit and date
   - Examination scope: Same as initial ingest strategy

2. **Compare commits:**
   ```bash
   # Get commit history between old and new
   gh api repos/owner/repo/compare/old-sha...new-sha --jq '{
     commits: .commits | length,
     files_changed: .files | length
   }'
   ```

3. **In raw file, document changes:**
   ```markdown
   ## Previous Ingest

   **Previous ingest date:** YYYY-MM-DD
   **Previous commit:** old-sha
   **Commits since:** N
   **Time elapsed:** X months

   **Conceptual changes since previous ingest:**
   - Architecture: [Stable | Evolved to X | Major change: Y → Z]
   - Goals: [Unchanged | Refined | Shifted to new focus]
   - Design philosophy: [Same | New emphasis on X]
   - New capabilities: [List]
   - Removed/deprecated: [List]
   - Documentation changes: [List]
   ```

4. **Update or supersede meta entries:**

   **If architecture fundamentally changed:**
   - Create new model with new date
   - In old model, add supersession notice:
     ```markdown
     **Status:** Superseded by meta/models/YYYY-MM-DD_repo-v2-architecture.md

     This architecture was replaced in [date] when project shifted from X to Y approach.
     Preserved for historical context.
     ```
   - In new model, reference evolution:
     ```markdown
     **Evolution:** This supersedes earlier architecture (meta/models/OLD-DATE_repo-architecture.md)
     See timeline: meta/timelines/repo-evolution.md
     ```

   **If architecture evolved but not fundamentally changed:**
   - Update existing model with revision note:
     ```markdown
     **Last revised:** YYYY-MM-DD (re-ingest, commit: new-sha)
     **Changes:** [Brief description of refinements]
     **Previous version:** [See git history for YYYY-MM-DD version]
     ```

5. **Create or update timeline:**
   ```markdown
   # Timeline: owner/repo Architectural Evolution

   ## YYYY-MM-DD (First ingest, commit: sha1)
   [Initial architecture description]

   ## YYYY-MM-DD (Re-ingest, commit: sha2)
   **Change:** [Explicit description of conceptual change]
   [Updated architecture description]
   ```

6. **Response to user:**
   ```
   **Repository re-ingested**

   Previous: YYYY-MM-DD (commit: old-sha)
   Current: YYYY-MM-DD (commit: new-sha)
   Time elapsed: X months, N commits

   **Conceptual changes detected:**
   - [Major change 1]
   - [Major change 2]

   **Meta updates:**
   - [Superseded old model | Updated existing model | No changes needed]
   - Timeline: [created | updated]

   **Assessment:** Architecture [stable | evolved | fundamentally changed]
   ```

---

### Case 3: Monorepo

**Detection:**
- Multiple `package.json`, `setup.py`, or other project files
- Workspace configuration files
- Directory structure suggests multiple projects
- README mentions "monorepo" or lists multiple packages

**Action: Clarify scope**
```
Monorepo detected: owner/repo

Projects identified:
1. packages/project-a - [Description from package.json]
2. packages/project-b - [Description]
3. packages/project-c - [Description]

Strategy:
1. Whole monorepo (Recommended if unified architecture)
   - Treat as single system
   - Focus on overall architecture and relationships
   - Describe how projects interact

2. Specific project (Select one)
   - Focus on single project within monorepo
   - Note its dependencies on other monorepo projects

3. Multiple ingests (Create separate ingests)
   - Ingest each project separately
   - Link related ingests

Which approach?
```

**If whole monorepo selected:**
- Raw file describes overall architecture
- Note how projects are organized and related
- Meta model describes monorepo architecture pattern
- List projects as components

**If specific project:**
- Raw file focuses on that project
- Note it's part of monorepo
- Reference other projects it depends on
- File naming: `YYYY-MM-DD_repo-slug_project-name.md`

**If multiple ingests:**
- Create separate raw file for each
- Cross-reference in each file
- Link meta entries appropriately

---

### Case 4: [UserName]'s Repository

**Detection:**
- User says "my repository" or "my repo"
- Repository URL contains [UserName]'s GitHub username (if known)
- User confirms when asked

**Action: Ask attribution**
```
Attribution: This repository appears to be authored by you ([UserName]).

How should I attribute the design decisions and architectural insights?

1. Origin: [UserName] (Recommended)
   - Your design decisions and architectural choices
   - I'm extracting and documenting your thinking
   - Most faithful to actual authorship

2. Origin: Co-created
   - I'm interpreting your code with analytical structure
   - Hybrid of your design + my interpretation

3. Origin: Fermi
   - Treat as external repository for objectivity
   - Useful if you want critical distance

Recommendation: Option 1 (Origin: [UserName])

Which attribution do you prefer?
```

**For Option 1 (Origin: [UserName]):**
```markdown
**Origin:** [UserName]

**Origin detail:**
This repository was created by [UserName].

Repository: https://github.com/[username]/repo (commit: sha)
Raw capture: raw/repos/YYYY-MM-DD_repo-slug.md
Design decisions: [UserName]
Extraction and organization: Claude (‹model›), YYYY-MM-DD

[UserName] designed this architecture and made these tradeoff decisions.
I extracted and structured the description from documentation and code.
```

**For Option 2 (Origin: Co-created):**
```markdown
**Origin:** Co-created

**Origin detail:**
Repository created by [UserName], interpreted and structured by Claude.

Repository: https://github.com/[username]/repo (commit: sha)
[UserName]'s work: Architecture design, implementation, documentation
Claude's work: Pattern extraction, tradeoff analysis, structural organization
Collaboration date: YYYY-MM-DD
```

**For Option 3 (Origin: Fermi):**
```markdown
**Origin:** Fermi (‹model›)

**Origin detail:**
Interpretive analysis of [UserName]'s repository, treated as external for objectivity.

Repository: https://github.com/[username]/repo (commit: sha)
Original author: [UserName]
Analysis: Claude (‹model›), YYYY-MM-DD
Treatment: Analyzed as external repository to maintain critical distance
```

---

### Case 5: Fork

**Detection:**
- Repository metadata shows `"isFork": true`
- Parent repository identified

**Action: Clarify treatment**
```
Fork detected: owner/repo
Parent repository: parent-owner/parent-repo

Strategy:
1. Independent (Recommended if substantial divergence)
   - Ingest as independent repository
   - Note fork origin in raw file
   - Focus on this fork's unique characteristics

2. Differential (If this is minor fork)
   - Document differences from parent
   - Requires parent to be ingested first
   - Focus on what changed

3. Cancel (Ingest parent instead)
   - If fork is not substantially different
   - Ingest parent repository instead

Which approach?
```

**If independent:**
- Normal ingest process
- In raw file, note:
  ```markdown
  **Fork information:**
  Parent repository: parent-owner/parent-repo
  Forked: YYYY-MM-DD
  Treatment: Independent (substantial divergence)
  ```

**If differential:**
- Check if parent ingested
- Document differences explicitly
- Link to parent ingest
- Meta entry focuses on what changed

---

### Case 6: Documentation Repository

**Detection:**
- Repository is primarily or entirely markdown files
- Structure suggests documentation site
- README indicates documentation purpose

**Action: Suggest alternative**
```
Documentation repository detected: owner/repo

This repository is primarily documentation (markdown files).

Recommended approach:
1. Use markdown ingest workflow instead (Recommended)
   - Ingest individual documentation files
   - Preserves structure better for retrieval
   - Use: INGEST_MARKDOWN.md workflow

2. Repository ingest (Alternative)
   - Treat as repository with all docs
   - Less granular for retrieval

Which approach do you prefer?
```

---

### Case 7: Archived Repository

**Detection:**
- Repository metadata shows `"isArchived": true`

**Action: Confirm intent**
```
Archived repository: owner/repo
Archived: YYYY-MM-DD
Status: No longer maintained

This repository is archived and no longer active.

Proceed with ingest?
1. Yes - Ingest as historical reference
2. Cancel - Look for maintained alternative
```

**If yes:**
- Normal ingest process
- In raw file, prominently note:
  ```markdown
  **Repository status:** ARCHIVED (YYYY-MM-DD)

  This repository is no longer maintained. Architecture and design decisions
  preserved as historical reference.
  ```
- In meta entries, note archived status

---

## Integration with Other Workflows

### After Repository Ingest, Check For:

1. **Contradictions** (CONTRADICTIONS.md)
   - Does this repository's approach conflict with existing KB claims?
   - Different solutions to same problem
   - Contradictory design philosophies

2. **Synthesis opportunities** (SYNTHESIS.md)
   - Does this unify with existing architectural models?
   - Cross-domain pattern recognition
   - General principles emerging

3. **Timeline updates** (TIMELINES.md)
   - If re-ingest: Track architectural evolution
   - If related to existing KB topic: Evolution of understanding

4. **Connection detection** (CONNECTIONS.md)
   - Structural similarities across repositories
   - Scale-crossing (abstract pattern ↔ concrete implementation)
   - Problem-solution patterns

---

## Examples

### Example 1: Small Library (Full Examination)

**User:** "Ingest https://github.com/example/small-parser"

**Process:**
```
Analyzing repository: example/small-parser...

Repository info:
- Type: Library
- Language: Rust
- Files: ~60 (estimated)
- Size: Small library

Strategy: Full examination (docs + structure + code samples)

Reading documentation:
✓ README.md (overview, goals, usage examples)
✓ No ARCHITECTURE.md found
✓ docs/design-decisions.md (rationale for parser approach)

Examining structure:
✓ Root layout: src/, tests/, examples/, docs/
✓ Entry point: src/lib.rs
✓ Core modules: src/parser.rs, src/lexer.rs, src/ast.rs

Sampling code:
✓ src/lib.rs (public API, 120 lines)
✓ src/parser.rs (core parser, 350 lines)
✓ src/lexer.rs (lexer implementation, 200 lines)

Files examined: 8 / 62 (13%)
Documentation: Complete
Structure: Complete
Code: Entry point + 2 core modules

Storing...
✓ raw/repos/2026-01-22_example_small-parser.md

Extracting architecture...
✓ meta/models/2026-01-22_small-parser-recursive-descent.md

Key insight: Uses recursive descent parser with explicit error recovery.
Design tradeoff: Clarity over performance (noted in docs/design-decisions.md).

Index updates:
✓ Tags: architecture:recursive-descent, pattern:error-recovery, tech:rust
✓ Entities: example/small-parser
✓ Glossary: recursive-descent, error-recovery, AST

Connection detected:
- This parser's error recovery strategy (continue on error, collect all errors)
  similar to your linter architecture model (collect all issues, don't stop).
  → Pattern: Collect-all-errors vs fail-fast tradeoff appears in multiple domains

**Repository ingested successfully**

Repository: example/small-parser (Rust library, 62 files)
Examined: README, design docs, structure, entry point + 2 core modules (13%)

Architectural insight: Recursive descent parser prioritizing clarity and comprehensive
error reporting over performance. Explicit design decision to accept slower parsing
for better error messages.

Meta created:
- meta/models/2026-01-22_small-parser-recursive-descent.md (Origin: Fermi)
  Recursive descent architecture with error recovery

Citation: `raw/repos/2026-01-22_example_small-parser.md`
```

---

### Example 2: Large Framework (Documentation-Only)

**User:** "Ingest https://github.com/facebook/react"

**Process:**
```
Analyzing repository: facebook/react...

Repository info:
- Type: Framework
- Language: JavaScript (TypeScript)
- Files: >5000 (estimated)
- Size: Very large framework

This is a very large repository (>5000 files).

Recommended approach:
1. Documentation-only (Recommended)
2. Targeted examination
3. Cancel

[User selects: 1]

Strategy: Documentation-only examination

Reading documentation:
✓ README.md (overview, goals, philosophy)
✓ docs/ARCHITECTURE.md (high-level architecture)
✓ docs/DESIGN_PRINCIPLES.md (design philosophy)
✓ docs/RENDERING.md (rendering model)
✓ CONTRIBUTING.md (patterns and conventions)

Examining structure:
✓ Root layout: packages/ (monorepo), docs/, fixtures/
✓ Packages: react, react-dom, react-reconciler, scheduler, others

Code sampling: None (large repository, documentation-focused)

Files examined: 8 / 5000+ (0.16%, documentation only)

Storing...
✓ raw/repos/2026-01-22_facebook_react.md

Extracting architecture...
✓ meta/models/2026-01-22_react-fiber-architecture.md
✓ meta/models/2026-01-22_react-reconciliation-model.md

Key insights:
- Fiber architecture: Incremental rendering with priority scheduling
- Reconciliation: Virtual DOM diffing algorithm
- Design philosophy: Declarative, composition over inheritance

Index updates:
✓ Tags: architecture:fiber, pattern:virtual-dom, pattern:reconciliation
✓ Entities: facebook/react, React, Fiber
✓ Glossary: fiber, reconciliation, virtual-dom, scheduling

**Repository ingested successfully**

Repository: facebook/react (JavaScript framework, 5000+ files)
Examined: Documentation only (README, architecture docs, design principles)

Transparency: 5000+ implementation files not examined. This model is based on
stated architecture from documentation. Implementation details not verified.

Architectural insights:
- Fiber architecture enables incremental rendering with priority scheduling
- Reconciliation algorithm optimizes updates via virtual DOM diffing
- Design prioritizes declarative patterns and composition

Meta created:
- meta/models/2026-01-22_react-fiber-architecture.md (Origin: Fermi)
  Fiber architecture with incremental rendering
- meta/models/2026-01-22_react-reconciliation-model.md (Origin: Fermi)
  Virtual DOM reconciliation algorithm

Scope note: Models based on documentation. Implementation at scale not examined.

Citation: `raw/repos/2026-01-22_facebook_react.md`
```

---

### Example 3: [UserName]'s Repository (Origin Attribution)

**User:** "Ingest my epidemiology modeling repository"

**Process:**
```
Analyzing repository: [username]/epi-model...

Attribution: This repository is authored by you ([UserName]).

How should I attribute the design decisions?
1. Origin: [UserName] (Recommended)
2. Origin: Co-created
3. Origin: Fermi

[User selects: 1]

Continuing with Origin: [UserName]...

Repository info:
- Type: Application
- Language: Python
- Files: ~150 (estimated)

Strategy: Medium examination (docs + structure + selective samples)

Reading documentation:
✓ README.md (model overview, equations, assumptions)
✓ docs/model-design.md (mechanistic structure)
✓ docs/calibration.md (parameter fitting approach)

Examining structure:
✓ Root layout: src/, tests/, data/, docs/, notebooks/
✓ Entry point: src/main.py
✓ Core modules: src/model/, src/calibration/, src/visualization/

Sampling code:
✓ src/main.py (entry point)
✓ src/model/compartmental.py (core model structure)

Files examined: 12 / 150 (8%)

Storing...
✓ raw/repos/2026-01-22_[username]_epi-model.md

Extracting architecture...
✓ meta/models/2026-01-22_epi-model-compartmental-structure.md

Origin: [UserName] (your design decisions)

Key insight: Age-structured compartmental model with hierarchical Bayesian calibration.
Design tradeoff: Complexity of age structure justified by fitting multiple data streams.

Index updates:
✓ Tags: domain:epidemiology, pattern:compartmental-model, pattern:hierarchical-bayes
✓ Entities: [username]/epi-model
✓ Glossary: compartmental-model, hierarchical-bayesian-calibration

**Repository ingested successfully**

Repository: [username]/epi-model (Python application, 150 files)
Examined: Documentation, structure, entry point + 1 core module (8%)

Architectural insight: Age-structured compartmental epidemiology model with hierarchical
Bayesian calibration. Design explicitly balances model complexity against ability to fit
multiple heterogeneous data streams.

Meta created:
- meta/models/2026-01-22_epi-model-compartmental-structure.md (Origin: [UserName])
  Age-structured compartmental model with hierarchical calibration

Origin: [UserName] designed this architecture. I extracted and structured the description.

Citation: `raw/repos/2026-01-22_[username]_epi-model.md`
```

---

### Example 4: Re-ingest After Major Update

**User:** "Re-ingest https://github.com/example/evolving-system"

**Process:**
```
Analyzing repository: example/evolving-system...

Previously ingested: 2025-08-15 (commit: abc123)
Current commit: def456 (145 commits ahead)
Time elapsed: 5 months

Strategy:
1. Full re-ingest
2. Cancel

[User selects: 1]

Continuing with full re-ingest...

Reading documentation:
✓ README.md (updated: now emphasizes streaming architecture)
✓ ARCHITECTURE.md (rewritten: batch → streaming migration)
✓ docs/migration-guide.md (new: explains transition)

Examining structure:
✓ Major restructure detected:
  - Old: src/batch/ (removed)
  - New: src/streaming/, src/event-bus/

Comparing architectures:
Previous (2025-08-15): Batch processing with scheduled jobs
Current (2026-01-22): Event-driven streaming with real-time processing

Storing...
✓ raw/repos/2026-01-22_example_evolving-system.md
  (includes section: Previous Ingest with comparison)

Architectural analysis:
✓ This is a fundamental change: batch → streaming
✓ Previous model should be superseded, not just updated

Creating timeline:
✓ meta/timelines/evolving-system-architecture-evolution.md

Superseding old model:
✓ Updated: meta/models/2025-08-15_evolving-system-batch.md
  (added supersession notice)
✓ Created: meta/models/2026-01-22_evolving-system-streaming.md
  (references timeline and previous architecture)

Index updates:
✓ Updated tags: removed batch-processing, added event-driven, streaming
✓ Timeline entry added to views

**Repository re-ingested successfully**

Previous: 2025-08-15 (commit: abc123, batch architecture)
Current: 2026-01-22 (commit: def456, streaming architecture)
Time elapsed: 5 months, 145 commits

**Conceptual changes detected:**
- Architecture: Fundamental change from batch to streaming
- Processing model: Scheduled jobs → event-driven real-time
- Design philosophy: Shift from periodic updates to continuous processing
- New components: Event bus, stream processors
- Removed: Batch job scheduler, periodic tasks

**Meta updates:**
- Superseded: meta/models/2025-08-15_evolving-system-batch.md
- Created: meta/models/2026-01-22_evolving-system-streaming.md (Origin: Fermi)
- Timeline: Created meta/timelines/evolving-system-architecture-evolution.md

**Assessment:** Architecture fundamentally changed (batch → streaming)

This represents a major architectural evolution. Previous batch-based model preserved
for historical context but marked as superseded. Timeline documents the transition.

Citation: `raw/repos/2026-01-22_example_evolving-system.md`
```

---

## Tools Reference

### GitHub CLI Commands

**Repository metadata:**
```bash
gh repo view owner/repo --json \
  nameWithOwner,description,url,\
  defaultBranchRef,primaryLanguage,languages,\
  createdAt,updatedAt,pushedAt,\
  isArchived,isFork,parent
```

**Current commit:**
```bash
gh api repos/owner/repo/commits/HEAD --jq '{
  sha: .sha,
  message: .commit.message,
  author_date: .commit.author.date
}'
```

**List directory:**
```bash
gh api repos/owner/repo/contents/path/to/dir --jq '.[] | "\(.type): \(.name)"'
```

**Fetch file:**
```bash
gh api repos/owner/repo/contents/path/to/file --jq '.content' | base64 -d
```

**Compare commits:**
```bash
gh api repos/owner/repo/compare/sha1...sha2 --jq '{
  commits: .commits | length,
  files_changed: .files | length
}'
```

**Check authentication:**
```bash
gh auth status
```

---

## Epistemic Discipline Checklist

Before completing repository ingest:

**Raw Layer:**
- [ ] Raw file created: `raw/repos/YYYY-MM-DD_repo-slug.md`
- [ ] Full provenance: URL, branch, commit, date, languages
- [ ] Examination scope explicitly stated
- [ ] What was examined listed with checkboxes
- [ ] What was skipped explicitly stated
- [ ] Rationale for scope provided
- [ ] Files examined count: N / M (percentage)
- [ ] Transparency: No silent omissions

**Origin Attribution:**
- [ ] Origin correct: Fermi (external) or [UserName] (his repo)
- [ ] If [UserName]'s repo: Asked for attribution preference
- [ ] Origin detail complete: Original authors, dates, interpretation noted
- [ ] Clear distinction: Design decisions vs interpretation

**Evidence vs Inference:**
- [ ] Raw file descriptive (what repository contains)
- [ ] Meta entries interpretive (architectural patterns inferred)
- [ ] Assumptions explicit in meta entries
- [ ] Uncertainties flagged (what wasn't examined, what remains unclear)
- [ ] Documentation-only ingests note: "Implementation not verified"

**Meta Layer:**
- [ ] Meta entries created (models primary, claims if applicable)
- [ ] Each meta entry has complete evidence base section
- [ ] Backlinks: meta → raw with specific sections referenced
- [ ] Meta entries use appropriate templates
- [ ] Scope notes added if partial examination

**Indexing:**
- [ ] Tags: 1-3 high-signal only (architecture, domain, pattern)
- [ ] Entities: Repository registered with description
- [ ] Glossary: Domain-specific terms added
- [ ] Link graph: Repository → meta links added

**Connections:**
- [ ] Checked for non-trivial connections only
- [ ] Filtered out generic/trivial similarities
- [ ] Connections are specific and add insight
- [ ] Cross-domain or scale-crossing preferred

**Integration:**
- [ ] Contradictions checked (conflicts with existing claims)
- [ ] Timeline created/updated if re-ingest with major changes
- [ ] Recent ingests updated
- [ ] Knowledge map updated if significant

**User Response:**
- [ ] Clear summary of examination scope
- [ ] Transparency about what wasn't examined
- [ ] Key architectural insights extracted (2-3 sentences)
- [ ] Meta entries listed with origins
- [ ] Index updates summarized
- [ ] Connections surfaced (if non-trivial)
- [ ] Citation format provided

**Re-ingest Specific:**
- [ ] Previous ingest referenced in raw file
- [ ] Conceptual changes noted explicitly
- [ ] Supersession handled if models replaced
- [ ] Timeline created if major architectural evolution
- [ ] Comparison: Architecture stability assessed

**Special Cases:**
- [ ] Large repos: Asked for strategy, transparency about scope
- [ ] Monorepos: Asked for strategy, clear about scope
- [ ] [UserName]'s repos: Asked for attribution
- [ ] Forks: Noted origin, asked for treatment
- [ ] Archived repos: Noted status prominently

---

## Integration Points

### With CONNECTIONS.md

After repository ingest:
- Check for structural similarity with existing models
- Check for contradictions with existing approaches
- Check for scale-crossing insights (implementation ↔ abstraction)
- Check for problem-solution patterns

### With CONTRADICTIONS.md

If repository contains claims conflicting with KB:
- Create contradiction entry
- Link both sources
- Document tension

### With TIMELINES.md

If re-ingest shows major conceptual change:
- Create or update timeline
- Document architectural evolution
- Show how design decisions changed

### With SYNTHESIS.md

If repository illuminates pattern across multiple existing models:
- Candidate for synthesis proposal
- Cross-domain architectural patterns
- General principles

---

## Status

**Status:** Fully Implemented (Phase 6)
**Created:** 2026-01-22
**Dependencies:**
- `gh` CLI (GitHub API access)
- Templates: `meta/models/_TEMPLATE.md`
- Workflows: CONNECTIONS.md, CONTRADICTIONS.md, TIMELINES.md
- Indices: tags.md, entities.md, glossary.md, link_graph.md
- Views: recent_ingests.md, knowledge_map.md (optional narrative)
- Router: `uv run scripts/generate_router.py` (regenerate after ingest)

---

## Summary

GitHub repository ingest captures intellectual content of codebases (goals, architecture, assumptions, tradeoffs) through selective examination with explicit transparency. Follows universal ingest pattern: preservation → extraction → linking → indexing → connection → views → response. Respects epistemic discipline: origin attribution, evidence vs inference, explicit scope, no silent omissions. Handles special cases: large repos, re-ingests, monorepos, [UserName]'s repos, forks. Integrates with connections, contradictions, timelines workflows.
