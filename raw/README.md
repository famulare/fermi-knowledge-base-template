# Raw Layer

The raw layer preserves original inputs with minimal transformation. This is the **fidelity layer** — treated as evidence.

## Principles

- **Append-only** except for redaction or provenance fixes
- **Verbatim preservation** — no silent editing
- **Provenance tracking** — every file has a clear source

## Directory Structure

- `chats/` — Conversation checkpoints
- `notes/` — Pasted markdown, written notes
- `repos/` — Repository ingest captures
- `web/` — Web content captures (papers, posts, reports, docs)
- `files/` — Imported files (PDFs, images, datasets)
- `curated/` — External content with clear attribution
- `provenance/` — File metadata and import records

## File Naming Convention

`YYYY-MM-DD_descriptive-slug.md`

Example: `2025-03-15_dose-response-model-notes.md`
