# Query Patterns - Common Grep Commands

Quick reference for grep-based retrieval in Fermi KB.

---

## Basic Searches

### Search Meta Layer by Keyword

```bash
grep -r "keyword" meta/ --include="*.md" -i
grep -r "keyword" meta/claims/ --include="*.md" -i
grep -r "keyword" meta/models/ --include="*.md" -i
```

### Search Raw Layer

```bash
grep -r "keyword" raw/ --include="*.md" -i
grep -r "keyword" raw/notes/ --include="*.md" -i
```

### Search Index Files

```bash
grep -i "keyword" index/tags.md
grep -i "keyword" index/entities.md
grep -i "keyword" index/glossary.md
```

---

## Pattern-Based Searches

### Find Claims by Origin

```bash
grep -r "Origin: [UserName]" meta/claims/ --include="*.md"
grep -r "Origin: Fermi" meta/claims/ --include="*.md"
grep -r "Origin: Co-created" meta/claims/ --include="*.md"
grep -r "Origin: External" meta/claims/ --include="*.md"
```

### Find by Status

```bash
grep -r "Status: Active" meta/claims/ --include="*.md"
grep -r "Status: Draft" meta/models/ --include="*.md"
grep -r "Status: Superseded" meta/ --include="*.md"
```

---

## Advanced Retrieval

### Multi-Keyword Search (AND)
```bash
grep -r "keyword1" meta/ --include="*.md" -l | xargs grep -l "keyword2"
```

### Multi-Keyword Search (OR)
```bash
grep -r -E "keyword1|keyword2" meta/ --include="*.md"
```

### Find Backlinks
```bash
grep -r "raw/notes/filename.md" meta/ --include="*.md"
```

### Find Uncertainties
```bash
grep -r "## Uncertainty" meta/ --include="*.md" -A 5
```

---

## Index-First Retrieval

1. Find tag in tags.md
2. Extract file paths
3. Read those specific files

---

## Relevance Ranking

1. Meta over raw (usually more structured)
2. Recent over old (unless temporal query)
3. Claims/Models over Maps (usually more specific)
4. Active over Superseded (unless tracking evolution)

---

## Count and Statistics

```bash
find meta/ -name "*.md" -not -name "*template*" -not -name "README.md" | wc -l
grep -r "Origin: Fermi" meta/ --include="*.md" | wc -l
grep -r "Origin: External" meta/ --include="*.md" | wc -l
```
