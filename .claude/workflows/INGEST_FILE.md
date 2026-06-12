# Workflow: File Import

**Trigger:** User references file path, uploads file, or says "ingest this file"

**Status:** Phase 5 - Fully Implemented

---

## Supported File Types

### Current Support

- **PDF files** (.pdf) - Text extraction with page numbers
- **Image files** (.png, .jpg, .jpeg, .gif, .webp) - Visual analysis via Claude's vision capabilities
- **Data files** (.csv, .json, .jsonl, .tsv) - Structure parsing and summary statistics
- **Text documents** (.txt, .md, .rst) - Direct text extraction
- **Document files** (.docx, .odt) - Text and structure extraction (when possible)

### Detection Strategy

File type determined by:
1. File extension (primary)
2. Content inspection if extension ambiguous
3. User specification if provided

---

## Process Steps

### Step 1: Validate and Prepare

**Check file exists:**
```bash
ls -lh "[file_path]"
```

**Get file metadata:**
```bash
# File size
du -h "[file_path]"

# File type
file "[file_path]"

# Checksum
shasum -a 256 "[file_path]"
```

**Confirm with user if large:**
```
File: [filename] ([size])
Type: [detected type]

This will be stored in raw/files/ and processed for meta extraction.
Proceed with import?
```

---

### Step 2: Store File in Raw Layer

**File naming:** `raw/files/YYYY-MM-DD_[original-filename.ext]`

**Storage:**
```bash
cp "[source_path]" "raw/files/YYYY-MM-DD_[filename].ext"
```

**Preservation principle:** Store original file verbatim, no modifications

---

### Step 3: Create Provenance Sidecar

**File naming:** `raw/provenance/YYYY-MM-DD_[original-filename].json`

**Generate metadata:**
```json
{
  "original_filename": "filename.ext",
  "original_path": "/path/to/source/file",
  "ingested_date": "YYYY-MM-DD",
  "ingested_time": "HH:MM:SS",
  "source_description": "user description or context",
  "file_type": "pdf|image|data|document|text",
  "checksum_sha256": "computed_hash",
  "size_bytes": 12345,
  "size_human": "1.2MB",
  "kb_location": "raw/files/YYYY-MM-DD_filename.ext",
  "metadata": {
    "author": "if_extractable",
    "created_date": "if_extractable",
    "modified_date": "from_filesystem",
    "title": "if_extractable",
    "pages": "if_pdf",
    "dimensions": "if_image",
    "format_version": "if_applicable"
  },
  "extraction_notes": "any issues or special handling"
}
```

**Write provenance:**
```bash
cat > "raw/provenance/YYYY-MM-DD_filename.json" << 'EOF'
[json content]
EOF
```

---

### Step 4: Parse Content (Format-Specific)

#### PDF Files (.pdf)

**Claude can read PDFs directly via Read tool.**

**Process:**
1. Read PDF using Read tool (returns text and visual content page by page)
2. Extract structure:
   - Identify sections, headings
   - Note figures, tables, equations
   - Preserve page numbers for citations
3. Identify content type:
   - Research paper → Extract claims, models, methods
   - Documentation → Extract key procedures, definitions
   - Report → Extract findings, recommendations
4. Flag extraction issues (scanned images, complex formatting)

**Citation format:**
```
raw/files/YYYY-MM-DD_paper.pdf:page-3
raw/files/YYYY-MM-DD_paper.pdf:pages-5-7
```

---

#### Image Files (.png, .jpg, etc.)

**Claude can read images directly via Read tool.**

**Process:**
1. Read image using Read tool (visual analysis)
2. Analyze content:
   - If contains text: Extract visible text
   - If diagram/flowchart: Describe structure and relationships
   - If data visualization: Extract data or describe patterns
   - If photo/screenshot: Describe relevant content
3. Determine what to extract:
   - Diagram → Create or update model with structure
   - Data viz → Extract data or create summary
   - Text image → Extract text to note
   - Screenshot → Describe and link to relevant topic

**Citation format:**
```
raw/files/YYYY-MM-DD_diagram.png (full image)
```

---

#### Data Files (.csv, .json, .jsonl, .tsv)

**Process:**

**For CSV/TSV:**
```bash
# Get dimensions
wc -l raw/files/YYYY-MM-DD_data.csv
head -1 raw/files/YYYY-MM-DD_data.csv | tr ',' '\n' | wc -l

# Preview structure
head -5 raw/files/YYYY-MM-DD_data.csv

# Basic statistics (if numeric)
# Generate summary in meta
```

**For JSON/JSONL:**
```bash
# Validate JSON
python3 -m json.tool raw/files/YYYY-MM-DD_data.json > /dev/null

# Get structure
cat raw/files/YYYY-MM-DD_data.json | python3 -c "import json, sys; print(json.load(sys.stdin).keys())"

# Get record count
cat raw/files/YYYY-MM-DD_data.jsonl | wc -l
```

**Extract to meta:**
- Schema description (columns/fields)
- Record count
- Key variables identified
- Summary statistics if applicable
- Intended use or context

---

#### Text Documents (.txt, .md, .rst)

**Process:**
```bash
# Read directly
cat raw/files/YYYY-MM-DD_document.txt
```

**Similar to markdown ingest:**
- Preserve verbatim in raw/files/
- Extract structure to meta layer
- Different from markdown ingest only in storage location

---

#### Document Files (.docx, .odt)

**Process (if tools available):**
```bash
# DOCX - extract to text
unzip -p raw/files/YYYY-MM-DD_document.docx word/document.xml | sed 's/<[^>]*>//g'

# Or use pandoc if available
pandoc raw/files/YYYY-MM-DD_document.docx -t markdown
```

**If tools not available:**
- Store file as-is
- Note in provenance: "Requires manual extraction or external tool"
- User can copy-paste content for ingestion if needed

---

### Step 5: Generate Meta Summary

**Determine meta entry type based on content:**

#### Research Paper/Technical Document → Claims + Models

**Extract:**
- Core claims with page citations
- Mechanistic models or frameworks
- Key findings
- Methods (if relevant to KB)
- Assumptions and limitations

**Create:**
- `meta/claims/YYYY-MM-DD_[claim-from-paper].md` for each major claim
- `meta/models/YYYY-MM-DD_[model-from-paper].md` if mechanistic model present

**Origin attribution:**
```markdown
**Origin:** [UserName] (ingested from [Author et al., Year])

**Origin detail:**
Ingested from paper: raw/files/YYYY-MM-DD_paper.pdf
Original author(s): [Names]
Publication: [Journal/Source, Year]
[UserName] chose to ingest this as part of KB on [date]
```

---

#### Dataset → Map + Glossary

**Create:**
- `meta/maps/[dataset-name].md` describing:
  - Schema and variables
  - Data collection context
  - Intended uses
  - Limitations
  - Link to raw file

**Add to glossary:**
- Key variables defined
- Domain-specific terms

---

#### Diagram/Visualization → Integrate with Existing Model/Map

**Process:**
1. Identify which existing model/map this illustrates
2. Update that model/map with:
   - Reference to diagram: `raw/files/YYYY-MM-DD_diagram.png`
   - Description of what diagram shows
   - How it relates to model

**If no existing model:**
- Create new model using diagram as evidence

---

#### Report/Documentation → Claims + Map

**Extract:**
- Key findings as claims
- Recommendations
- Procedures or frameworks as maps
- Context and scope

---

### Step 6: Create Backlinks

**In all meta entries created from file:**

```markdown
## Evidence Base

Primary source:
- `raw/files/YYYY-MM-DD_[filename].ext` (full file)
- `raw/files/YYYY-MM-DD_[filename].ext:page-3` (specific location)

Provenance: `raw/provenance/YYYY-MM-DD_[filename].json`
```

**For PDFs, use page numbers:**
```markdown
- `raw/files/YYYY-MM-DD_paper.pdf:page-5` - [What's on this page]
- `raw/files/YYYY-MM-DD_paper.pdf:pages-8-12` - [What's in this section]
```

**For images:**
```markdown
- `raw/files/YYYY-MM-DD_diagram.png` - [What diagram shows]
```

**For data files:**
```markdown
- `raw/files/YYYY-MM-DD_data.csv` - [Dataset description]
```

---

### Step 7: Update Indices

**Tags** (`index/tags.md`):
- Add 1-3 high-signal tags for new concepts
- Add file type tag if creating new domain: `file-type:pdf`, `file-type:dataset`

**Entities** (`index/entities.md`):
- Register paper authors (for academic papers)
- Register organizations or projects
- Register key concepts introduced

**Glossary** (`index/glossary.md`):
- Add technical terms from paper
- Add variable definitions from datasets
- Add domain-specific terminology

**Link Graph** (`index/link_graph.md`):
- Evidence → Claim links for extracted claims
- File → Model links for supporting diagrams
- Cross-reference with existing KB elements

---

### Step 8: Surface Connections

**Check for:**
- **Cross-domain similarities:** Does this paper's model resemble existing KB models?
- **Contradictions:** Does this conflict with existing claims?
- **Scale-crossing:** Does this provide micro detail for existing macro model (or vice versa)?
- **Synthesis opportunities:** Could this unify with existing understanding?

**Filter:** Only surface non-trivial connections (not just topical overlap)

---

### Step 9: Update Views

**Recent Ingests** (`views/persistent/recent_ingests.md`):

```markdown
### YYYY-MM-DD: [Filename or Title]
**Type:** File ([pdf|image|data|document])
**Raw location:** raw/files/YYYY-MM-DD_[filename].ext
**Provenance:** raw/provenance/YYYY-MM-DD_[filename].json
**Original author:** [if applicable - paper author, dataset creator]
**Meta entries:**
  - meta/claims/[...].md (Origin: [UserName], ingested from [Author])
  - meta/models/[...].md (Origin: [UserName], ingested from [Author])
**Key content:** [Brief summary of what was extracted]
**Connections surfaced:** [Count and types if any]
```

**Knowledge Map** (`views/persistent/knowledge_map.md`):
(Optional — for narrative overview only; `index/router.md` is the primary navigation surface.)
Update if file import opens a new domain area or adds significant evidence.

**Regenerate Router:**
After updating index files, regenerate the router to reflect changes:
```bash
uv run scripts/generate_router.py
```

---

### Step 10: Response to User

**Format:**
```
**File imported successfully**

Stored: raw/files/YYYY-MM-DD_[filename].ext ([size])
Provenance: raw/provenance/YYYY-MM-DD_[filename].json

**Content extracted:**
[Summary of what was extracted - e.g., "PDF with 15 pages, extracted 3 key
claims and 1 mechanistic model"]

**Meta entries created:**
- meta/claims/YYYY-MM-DD_[claim].md (Origin: [UserName], ingested from [Author])
  [Brief claim statement]
- meta/models/YYYY-MM-DD_[model].md (Origin: [UserName], ingested from [Author])
  [Brief model description]

**Index updates:**
- Added tags: [tag1], [tag2]
- Registered entities: [author name], [organization]
- Added to glossary: [N] terms

[If connections detected:]
**Connections detected:**
- [Connection 1 with brief rationale]
- [Connection 2 with brief rationale]

**Citation format for this file:**
`raw/files/YYYY-MM-DD_[filename].ext:page-X` (for PDFs)
`raw/files/YYYY-MM-DD_[filename].ext` (for other files)
```

---

## Special Handling

### Large Files

**If file > 10MB:**
```
File size: [size]

This is a large file. Should I:
1. Import and extract key content only (don't load full file into context)
2. Import and note for manual review later
3. Cancel import
```

**If importing large file:**
- Store in raw/files/ as usual
- Extract metadata only initially
- Note in provenance: "Large file, extract on demand"
- User can request specific page/section extraction later

---

### Scanned PDFs (Images, Not Text)

**If PDF is scanned images:**
```
Note: This PDF appears to be scanned images (not text-based).

I can:
1. Analyze visually (describe what I see on each page)
2. Note for later OCR processing
3. Extract manually (you provide key text)

Which approach do you prefer?
```

---

### Password-Protected Files

**If file requires password:**
```
File is password-protected.

Cannot extract content automatically. Should I:
1. Store file as-is with note "Requires password to extract"
2. Cancel import (you can extract first, then ingest extracted content)
```

---

### Binary Files Without Extractable Content

**If file is pure binary (compiled code, etc.):**
```
File type: [binary type]

No content extraction available. Should I:
1. Store file for reference with description you provide
2. Cancel import (if not useful without extraction)
```

---

## Examples

### Example 1: Academic Paper Import

**User:** "Ingest this paper on mechanistic models" [provides PDF path]

**Process:**
```
Reading PDF: mechanism_paper_2024.pdf (25 pages)...

Content analysis:
- Research paper
- 3 major claims identified
- 1 mechanistic model described (pages 8-12)
- Methods section (pages 5-7)
- Discussion of limitations (pages 20-22)

Storing...
✓ raw/files/2026-01-22_mechanism_paper_2024.pdf
✓ raw/provenance/2026-01-22_mechanism_paper_2024.json

Extracting structure...
✓ meta/claims/2026-01-22_mechanism-x-causes-y.md
✓ meta/claims/2026-01-22_pathway-a-to-b.md
✓ meta/models/2026-01-22_three-stage-mechanism.md

Index updates:
✓ Added tags: mechanistic-models, pathways, causation
✓ Registered entities: Smith et al. (2024)
✓ Added to glossary: pathway-specificity, mechanistic-intervention

Connection detected:
- This three-stage mechanism (Origin: [UserName], from Smith et al.) structurally
  similar to your two-layer architecture model (raw→meta→retrieval stages)
  → Potential: General pattern of staged processing

**File imported and meta structure created.**

Citations: Use `raw/files/2026-01-22_mechanism_paper_2024.pdf:page-X`
```

---

### Example 2: Diagram Import

**User:** "Ingest this diagram showing the system architecture" [provides PNG]

**Process:**
```
Reading image: system_architecture.png...

Visual analysis:
- System architecture diagram
- Shows 5 components with connections
- Labels indicate data flow
- Hierarchical structure (3 layers)

Storing...
✓ raw/files/2026-01-22_system_architecture.png
✓ raw/provenance/2026-01-22_system_architecture.json

This diagram appears to illustrate [existing model or new concept].

Should I:
1. Update existing model (meta/models/[model].md) with this diagram
2. Create new model based on this diagram
3. Add to a domain map

[User chooses option]

**Diagram stored and linked to [meta entry].**

Citation: `raw/files/2026-01-22_system_architecture.png`
```

---

### Example 3: Dataset Import

**User:** "Ingest this CSV with experiment results"

**Process:**
```
Reading file: experiment_results.csv...

Structure analysis:
- 1,245 rows (observations)
- 12 columns (variables)
- Key variables: treatment, outcome, control_group, measurement_date
- Numeric variables: outcome (range 0-100), sample_size (range 10-50)
- Categorical: treatment (3 levels), control_group (2 levels)

Storing...
✓ raw/files/2026-01-22_experiment_results.csv
✓ raw/provenance/2026-01-22_experiment_results.json

Creating dataset documentation...
✓ meta/maps/experiment-results-2024.md

Added to glossary:
✓ treatment, outcome, control_group (with definitions)

**Dataset imported and documented.**

The dataset shows: [brief summary of patterns if obvious]

Citation: `raw/files/2026-01-22_experiment_results.csv`
```

---

## Integration with Other Workflows

### After File Import, Check for:

1. **Contradictions** - Does imported content conflict with existing claims?
2. **Synthesis opportunities** - Does this unify with existing models?
3. **Timeline updates** - Does this represent evolution of understanding?

### File Import Can Trigger:

- Contradiction detection (if imported claim conflicts with existing)
- Synthesis proposals (if imported model unifies with existing)
- Timeline creation (if this is 2nd+ position on topic)

---

## Grouped Extraction Checklist

When extracting multiple documents into a single file (e.g., a folder of PDFs grouped by theme or time period):

1. **Hard boundaries:** Each source document gets its own clearly headed section. No narrative bridges that blur source boundaries.
2. **Per-source attribution:** Every finding, number, and claim must be explicitly tagged to its source document within the file.
3. **No cross-source inference in body:** Cross-document themes or synthesis belong in a clearly labeled "Cross-Document Themes" section at the end, not woven into individual source sections.
4. **Conflation self-check:** After extraction, review each source section and ask: "Could any claim in this section actually belong to an adjacent source?" Pay special attention to:
   - Geographic-specific results in multi-region collections
   - Temporal data in sequential reports (estimates that evolved over time)
   - Similar parameter names across related documents
5. **Supersession notes:** When a later document revises an estimate from an earlier one, explicitly note the supersession.
6. **Parameter provenance:** All quantitative values must include inline source annotation: `(source: page X / table Y / section Z of [document name])`.

---

## Epistemic Discipline Checklist

Before completing file import:

- [ ] File stored verbatim in raw/files/ (no modifications)
- [ ] Provenance sidecar created with complete metadata
- [ ] Origin attribution correct ([UserName], ingested from [Author])
- [ ] Citations use proper format (page numbers for PDFs)
- [ ] Backlinks from meta to raw file included
- [ ] Only high-signal tags added (1-3 typically)
- [ ] Entities registered (authors, organizations)
- [ ] Non-trivial connections surfaced (if any)
- [ ] Recent ingests updated
- [ ] User receives clear summary of what was extracted
- [ ] Raw purity: no forward-looking synthesis or editorial interpolation in extraction body
- [ ] Parameter provenance: all quantitative values have inline source annotations
- [ ] Grouped extraction: conflation self-check completed (if multiple sources)
