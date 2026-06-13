# OKF Epistemic Profile (v0.1-draft)

**Status:** Draft — awaiting review/lock. Not yet submitted upstream.
**Extends:** Open Knowledge Format **v0.1** — `GoogleCloudPlatform/knowledge-catalog`
@ `ee67a5ca27044ebe7c38385f5b6cffc2305a9c1a` (the spec this profile pins to).
**Relationship to OKF:** a strict, fully **back-compatible overlay**. Every addition below is
either an OKF *additional frontmatter key* or a *link title* — both of which OKF consumers are
required to tolerate. A vanilla OKF tool reads a profile bundle without modification; a
profile-aware tool enforces the extra rules.
**Intent:** a **handoff**, not a land-grab. Offered to the OKF maintainers to fold in (or be
inspired by). No spec ownership sought. Reference implementation: this template's
`scripts/okf_export.py`, `scripts/okf_import.py`, `scripts/okf_validate.py`.

---

## 1. Why

OKF v0.1 standardizes the *bones* of an LLM-maintained knowledge wiki (markdown + YAML
frontmatter + `index.md`/`log.md` + a cross-link graph) and is **deliberately permissive**:
the only required field is `type`, and consumers MUST tolerate missing fields, unknown types,
unknown keys, and broken links. That permissiveness is the right call for a *lingua franca*.

It also means OKF says nothing about the layer that decides whether a knowledge base stays
**trustworthy** as it grows and is partly agent-generated: *who* asserted a thing and *how
sure* we are; whether something is evidence or interpretation; whether two claims conflict;
whether a claim has been superseded. This profile adds exactly that layer, and nothing else.

The sharpest place it matters is the **consume** direction: an OKF bundle is, by design,
low-provenance and possibly agent-generated, so importing one safely is the "treat extractions
as hypotheses, not facts" problem. The profile is the metadata that makes that quarantine
possible.

## 2. Conformance

A bundle **conforms to the OKF Epistemic Profile** if and only if:

1. It is **conformant with OKF v0.1** (parseable YAML frontmatter on every non-reserved `.md`;
   non-empty `type`; reserved files well-formed). — *inherited, unchanged.*
2. Every non-reserved concept document carries a valid **`origin`** (§3.1), with the
   contradiction exemption in §3.1.
3. Every non-reserved concept document carries a **`status`** drawn from the taxonomy for its
   `type` (§3.2).
4. Every concept document carries a **`layer`** (§3.3).
5. Typed relations, where present, use the **`rel:<verb>` link-title** convention (§4) with a
   verb from the bundle's referenced **verb registry**.
6. A conforming **validator** (§5) is available to check 1–5.

A profile-aware consumer **MUST** still honor OKF's tolerance rules (it MUST NOT reject a
bundle merely for *OKF* reasons); profile violations are reported by the validator, not by
refusing to read.

## 3. Frontmatter additions (all OKF "additional keys")

### 3.1 `origin` (required; contradictions exempt)
Who authored the concept. Validated by **prefix/base**, not exact string:

| base | meaning |
|---|---|
| `<Owner>` (e.g. a person's name/handle) | first-party human authorship |
| `Fermi (<model>)` / `<AI> (<model>)` | AI synthesis, model named |
| `Co-created (<Owner> + <AI> (<model>))` | joint authorship |
| `External (<Author/Org>)` | someone else's work |

- The **full** origin string (which may carry citations, dates, mixed authorship) is preserved
  verbatim in **`origin_detail`** when it is richer than the base.
- For `External` origin, include where known: `original_author`, `original_source`,
  `ingest_reason`, `ingest_date`.
- **Contradiction exemption:** a contradiction concept records a *tension between* other
  concepts and need not carry a single top-level `origin`. Its per-item provenance is carried
  as an `items[]` block (each with its own `origin`/`source`/`raw_evidence`) or preserved
  verbatim in the body.

### 3.2 `status` (required)
The epistemic lifecycle state. Taxonomy is `type`-scoped:

- claims / models / maps: `Draft` | `Active` | `Exploratory` | `Reflection` | `Superseded` |
  `Archived` (models additionally allow `Proposed`)
- contradictions: `Open` | `Resolved` | `Coexisting` | `Productive tension`
- timelines: `Draft` | `Active` | `Superseded` | `Archived`

`status` carries the **base** value. Any annotation (e.g. `Active — under revision`) is
preserved in **`status_note`**. Rationale: an explicit lifecycle makes *staleness* and
*supersession* representable, which a bare last-modified `timestamp` cannot.

### 3.3 `layer` (required)
The evidence/interpretation firewall: `raw` | `meta` (`examples` permitted as a
demonstrative sub-label of `meta`).

- `raw` = preserved evidence, **append-only, never synthesized into**.
- `meta` = interpretation (claims/models/maps/contradictions/timelines), always traceable to
  `raw`.

This is the structural anti-confabulation mechanism: confabulation enters through raw/meta
confusion, so making the boundary explicit turns it into a *detectable category error*.

## 4. Typed relations — `rel:<verb>` link titles

OKF states a link's relationship kind "is conveyed by the surrounding prose, not by the link
itself," and consumers treat links as untyped directed edges. This profile makes the type
**machine-readable without changing the link** by carrying it in the standard CommonMark
**link title**:

```markdown
[Continuous Immunity Framework](/models/model_continuous_immunity_framework.md "rel:supersedes")
```

- The `href` is unchanged, so a vanilla OKF consumer's graph is identical (it sees a normal
  untyped directed edge; the title is an ignorable tooltip).
- **Parse rule (one line):** *a link title matching `rel:<verb>` is a typed edge, classified by
  looking `<verb>` up in the verb registry → {relation class, direction}; any other title or no
  title ⇒ untyped associative link.*
- The **verb registry** is referenced, not invented per-bundle: this template ships
  [`index/edge_verbs.md`](index/edge_verbs.md) (canonical verb → inverse, class, directionality),
  with **7 relation classes**: evidential, structural, tension, synthesis, supersession,
  associative, potential. The verb encodes direction (`supersedes` vs `superseded-by`), so no
  extra direction marker is needed.
- Typed relations are **canonical at the point of assertion** (on the link). A derived edge
  index (e.g. `graph.json`) is generated *from* the bundle, never the source of truth —
  mirroring "markdown canonical, everything derived."

## 5. Validator (required)

Because OKF ships no validator, the profile requires one. It MUST check OKF base conformance
(§2.1) **and** the profile rules (§2.2–2.5), and MUST **exempt reserved files** (`index.md`,
`log.md`) from the `type` check. Reference implementation: `scripts/okf_validate.py` (reusing
the structural checks in `scripts/kb_audit.py`).

## 6. Back-compatibility (normative)

- Every key in §3 is an OKF *additional frontmatter key*; OKF consumers "should preserve
  unknown fields and not reject documents with unrecognized fields."
- The §4 convention rides inside the link **title**; OKF consumers treat the link as an untyped
  directed edge regardless.
- Therefore **every profile bundle is an OKF bundle.** The profile only *adds* obligations on
  producers and profile-aware consumers; it removes none of OKF's tolerance guarantees.

## 7. Reference implementation & worked example

- **Export** (`scripts/okf_export.py`): emits a profile bundle from a Fermi knowledge base.
- **Import** (`scripts/okf_import.py` + `.claude/workflows/INGEST_OKF.md`): consumes a bundle
  as *evidence* into an append-only raw layer and synthesizes attributed interpretation —
  never auto-promoting bundle assertions to first-party fact (the §1 quarantine).
- **Validate** (`scripts/okf_validate.py`): §5.
- The shipped `examples/` corpus exports to a small worked profile bundle suitable for
  rendering in OKF's own visualizer.

## 8. Open questions (for review)

- **`rel:` carries the verb** (registry → class+direction), not the class name. Confirm vs.
  carrying a class token directly.
- **`layer` values**: `{raw, meta}` with `examples` as a `meta` sub-label — vs. promoting
  `examples` to a first-class value.
- **Known lossy points** (declared, not hidden): sub-document epistemic typing
  (evidence/inference/interpolation *within* a concept) and per-edge rationale prose are not
  expressible in frontmatter/link-title and remain in the body. The validator/export print the
  declared-dropped set rather than silently losing it.
- **Submission form**: contribute as a formal OKF extension (lives in their governance) vs. an
  independent profile that targets OKF conformance. Default: offer it; let the maintainers
  decide where it lives.
