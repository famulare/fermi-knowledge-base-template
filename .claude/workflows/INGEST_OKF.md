# Workflow: OKF Bundle Ingest

**Trigger:** User wants to consume an external Open Knowledge Format (OKF) bundle into the KB

**Status:** Implemented 2026-06-13

---

## Purpose

Bring an external **OKF bundle** (`GoogleCloudPlatform/knowledge-catalog`; see
`OKF_EPISTEMIC_PROFILE.md`) into the KB **as evidence, never as fact**. OKF is permissive by
design — a bundle may be agent-generated and carries no required provenance — so importing one
is exactly the "treat extractions as hypotheses, not facts" problem. This workflow quarantines
the bundle and routes interpretation through human review.

**Key distinction from other ingest workflows:**
- `INGEST_CURATED` is for a single external document with a clear author.
- `INGEST_OKF` is for a *structured bundle of concepts* whose internal attributions are
  themselves untrusted; the whole bundle is treated as one external evidence source.

---

## When to Use This Workflow

- Someone hands you an OKF bundle (a directory of markdown concept files + `index.md`/`log.md`).
- A tool (e.g. OKF's reference enrichment agent) generated a bundle you want to draw on.
- You want to evaluate another system's knowledge without adopting its claims as your own.

---

## Steps

### 1. Land the bundle as quarantined evidence
```
uv run scripts/okf_import.py <bundle_dir> --org "<source org>" \
    --source "<url/citation>" --reason "<why you're ingesting>"
```
This **fails closed** on unsafe input (symlinks, path traversal, oversize/too-many files,
non-UTF-8). On success it:
- copies the bundle **verbatim** to `raw/curated/okf/<name>/` (append-only; refuses to
  overwrite an existing import without `--force`);
- writes `_PROVENANCE.md` (`Origin: External (<org>)`, source, ingest date, trust note);
- writes a **synthesis proposal** to `views/ephemeral/okf-import-<name>.md`.

Use `--dry-run` first to preview counts and the landing path.

### 2. Review the synthesis proposal (human, required)
Open `views/ephemeral/okf-import-<name>.md`. It lists each concept as a *candidate* with a
suggested type/title, a suggested `Origin: External (<org>)` (the bundle's own stated origin is
shown but **not trusted**), and the raw path. **Nothing is fact until you promote it.**

### 3. Promote selectively via the normal workflows
For each candidate worth keeping, create a meta entry the usual way (`INGEST_CURATED` /
`INGEST_MARKDOWN` / claim or model templates), with:
- `Origin: External (<org>)` — or `Co-created` if you add your own interpretation;
- **`Status: Draft` or `Exploratory` — never `Active`** without independent corroboration;
- an Evidence link back to the quarantined `raw/curated/okf/<name>/...` source.

### 4. Audit
Run `uv run scripts/kb_audit.py` after promotion. Promoted entries must satisfy the usual
status–evidence rules (an Active claim needs raw evidence; imported material starts un-promoted).

---

## Invariants (why this is safe)

- **Raw purity:** the bundle lands in `raw/`, append-only, never synthesized into.
- **Propose-only:** `okf_import.py` writes evidence + a proposal; it never writes `meta/`.
  Promotion is always a human step.
- **Untrusted attribution:** the bundle's internal `origin` fields are surfaced for context but
  re-attributed to `External` on import — a bundle cannot assert first-party authorship into
  your KB.
- **Status floor:** promoted entries start Draft/Exploratory.

---

## Related

- `OKF_EPISTEMIC_PROFILE.md` — the profile this consumes/produces
- `scripts/okf_import.py` — the importer
- `scripts/okf_export.py` — the reverse direction (KB → OKF bundle)
- `scripts/okf_validate.py` — bundle conformance check
- `.claude/workflows/INGEST_CURATED.md` — promotion path for individual concepts
