#!/usr/bin/env python3
"""SQLite FTS5 search CLI for the Fermi knowledge base.

Provides full-text search over the KB's markdown corpus with heading-based
chunking, metadata extraction, and ranked retrieval.

The database is a disposable derived artifact — fully rebuildable from the
markdown corpus. Markdown is the canonical source of truth.

Usage:
    uv run scripts/kb_search.py rebuild                      # Full rebuild
    uv run scripts/kb_search.py search "dose response model"  # Search
    uv run scripts/kb_search.py search "query" --layer meta   # Filter by layer
    uv run scripts/kb_search.py read 42                       # Read chunk by ID
    uv run scripts/kb_search.py status                        # DB stats + staleness
"""

from __future__ import annotations

import argparse
import os
import re
import sqlite3
import sys
import textwrap
from datetime import datetime, timedelta
from pathlib import Path

# Directories to index
CONTENT_DIRS = [
    "examples",
    "raw",
    "meta",
    "special_projects",
    "views/persistent",
]

# Default database path (relative to repo root)
DB_REL_PATH = "index/kb_index.db"

# Chunking parameters
MAX_CHUNK_WORDS = 1500  # Split sections exceeding this
TARGET_SPLIT_WORDS = 600  # Approximate split point for oversized sections
MIN_FILE_WORDS_FOR_CHUNKING = 500  # Files smaller than this become one chunk


def find_repo_root() -> Path:
    """Find the repository root by looking for CLAUDE.md."""
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / "CLAUDE.md").exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent


def get_db_path(repo_root: Path) -> Path:
    return repo_root / DB_REL_PATH


# --- Schema ---


def create_schema(conn: sqlite3.Connection):
    """Create the chunks and FTS5 tables."""
    conn.executescript(
        """
        DROP TABLE IF EXISTS chunks_fts;
        DROP TABLE IF EXISTS chunks;
        DROP TABLE IF EXISTS rebuild_meta;

        CREATE TABLE chunks (
            chunk_id     INTEGER PRIMARY KEY,
            file_path    TEXT NOT NULL,
            heading      TEXT,
            heading_level INTEGER DEFAULT 0,
            line_start   INTEGER NOT NULL,
            line_end     INTEGER NOT NULL,
            word_count   INTEGER NOT NULL,
            content      TEXT NOT NULL,
            layer        TEXT NOT NULL,
            sublayer     TEXT,
            origin       TEXT,
            status       TEXT,
            date         TEXT,
            file_size    INTEGER NOT NULL
        );

        CREATE VIRTUAL TABLE chunks_fts USING fts5(
            heading,
            content,
            file_path,
            content=chunks,
            content_rowid=chunk_id,
            tokenize='porter unicode61'
        );

        CREATE TABLE rebuild_meta (
            key   TEXT PRIMARY KEY,
            value TEXT
        );
    """
    )


# --- Metadata Extraction ---


def extract_date_from_filename(filepath: Path) -> str | None:
    """Extract YYYY-MM-DD from filename."""
    m = re.match(r"(\d{4}-\d{2}-\d{2})", filepath.name)
    return m.group(1) if m else None


def classify_layer(rel_path: str) -> tuple[str, str | None]:
    """Classify file into layer/sublayer."""
    parts = rel_path.split("/")
    layer = parts[0]
    if layer == "views":
        return "views", None
    sublayer = parts[1] if len(parts) > 2 else None
    return layer, sublayer


def extract_metadata(text: str) -> dict[str, str | None]:
    """Extract Origin and Status fields from file content."""
    origin = None
    status = None

    for line in text.split("\n")[:50]:  # Only check first 50 lines
        line = line.strip()
        if line.startswith("**Origin:**"):
            origin = line.replace("**Origin:**", "").strip()
        elif line.startswith("Origin:"):
            origin = line.replace("Origin:", "").strip()
        if line.startswith("**Status:**"):
            status = line.replace("**Status:**", "").strip()
        elif line.startswith("Status:"):
            status = line.replace("Status:", "").strip()

    return {"origin": origin, "status": status}


# --- Chunking ---


def chunk_file(filepath: Path, repo_root: Path) -> list[dict]:
    """Split a markdown file into heading-delimited chunks.

    Rules:
    - Chunk at H1/H2/H3 boundaries
    - Preamble (before first heading) is its own chunk
    - Sections >MAX_CHUNK_WORDS with no sub-headings split at paragraphs
    - Files <MIN_FILE_WORDS_FOR_CHUNKING become a single chunk
    """
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
    except OSError:
        return []

    if not lines:
        return []

    rel_path = str(filepath.relative_to(repo_root))
    file_size = filepath.stat().st_size
    layer, sublayer = classify_layer(rel_path)
    date = extract_date_from_filename(filepath)

    full_text = "".join(lines)
    total_words = len(full_text.split())

    # Small files: single chunk
    if total_words < MIN_FILE_WORDS_FOR_CHUNKING:
        meta = extract_metadata(full_text)
        # Extract title from first heading if present
        heading = None
        heading_level = 0
        for line in lines:
            m = re.match(r"^(#{1,3})\s+(.+)$", line.rstrip())
            if m:
                heading = m.group(2).strip()
                heading_level = len(m.group(1))
                break
        return [
            {
                "file_path": rel_path,
                "heading": heading,
                "heading_level": heading_level,
                "line_start": 1,
                "line_end": len(lines),
                "word_count": total_words,
                "content": full_text,
                "layer": layer,
                "sublayer": sublayer,
                "origin": meta["origin"],
                "status": meta["status"],
                "date": date,
                "file_size": file_size,
            }
        ]

    # Find heading positions
    headings = []
    for i, line in enumerate(lines):
        m = re.match(r"^(#{1,3})\s+(.+)$", line.rstrip())
        if m:
            headings.append(
                {
                    "level": len(m.group(1)),
                    "text": m.group(2).strip(),
                    "line_idx": i,  # 0-based
                }
            )

    if not headings:
        # No headings: single chunk (regardless of size)
        meta = extract_metadata(full_text)
        return [
            {
                "file_path": rel_path,
                "heading": None,
                "heading_level": 0,
                "line_start": 1,
                "line_end": len(lines),
                "word_count": total_words,
                "content": full_text,
                "layer": layer,
                "sublayer": sublayer,
                "origin": meta["origin"],
                "status": meta["status"],
                "date": date,
                "file_size": file_size,
            }
        ]

    # Build sections from headings
    sections = []

    # Preamble: content before first heading
    if headings[0]["line_idx"] > 0:
        preamble_lines = lines[: headings[0]["line_idx"]]
        preamble_text = "".join(preamble_lines)
        if preamble_text.strip():
            sections.append(
                {
                    "heading": None,
                    "heading_level": 0,
                    "line_start": 1,
                    "line_end": headings[0]["line_idx"],
                    "text": preamble_text,
                }
            )

    # Content sections
    for i, h in enumerate(headings):
        start_idx = h["line_idx"]
        if i + 1 < len(headings):
            end_idx = headings[i + 1]["line_idx"]
        else:
            end_idx = len(lines)

        section_lines = lines[start_idx:end_idx]
        section_text = "".join(section_lines)

        sections.append(
            {
                "heading": h["text"],
                "heading_level": h["level"],
                "line_start": start_idx + 1,  # 1-based
                "line_end": end_idx,
                "text": section_text,
            }
        )

    # Convert sections to chunks, splitting oversized ones
    chunks = []
    file_meta = extract_metadata(full_text)

    for section in sections:
        section_words = len(section["text"].split())

        if section_words <= MAX_CHUNK_WORDS:
            chunks.append(
                {
                    "file_path": rel_path,
                    "heading": section["heading"],
                    "heading_level": section["heading_level"],
                    "line_start": section["line_start"],
                    "line_end": section["line_end"],
                    "word_count": section_words,
                    "content": section["text"],
                    "layer": layer,
                    "sublayer": sublayer,
                    "origin": file_meta["origin"],
                    "status": file_meta["status"],
                    "date": date,
                    "file_size": file_size,
                }
            )
        else:
            # Split at paragraph boundaries near TARGET_SPLIT_WORDS
            sub_chunks = split_oversized_section(
                section, rel_path, layer, sublayer, file_meta, date, file_size, lines
            )
            chunks.extend(sub_chunks)

    return chunks


def split_oversized_section(
    section: dict,
    rel_path: str,
    layer: str,
    sublayer: str | None,
    file_meta: dict,
    date: str | None,
    file_size: int,
    all_lines: list[str],
) -> list[dict]:
    """Split an oversized section at paragraph boundaries."""
    start_idx = section["line_start"] - 1  # Convert to 0-based
    end_idx = section["line_end"]
    section_lines = all_lines[start_idx:end_idx]

    chunks = []
    current_chunk_lines: list[str] = []
    current_start = start_idx
    word_count = 0

    for i, line in enumerate(section_lines):
        current_chunk_lines.append(line)
        word_count += len(line.split())

        # Check for paragraph boundary (blank line) near target
        is_blank = not line.strip()
        at_end = i == len(section_lines) - 1

        if (is_blank and word_count >= TARGET_SPLIT_WORDS) or at_end:
            chunk_text = "".join(current_chunk_lines)
            actual_words = len(chunk_text.split())
            if actual_words > 0:
                # For continuation chunks, annotate the heading
                heading = section["heading"]
                chunk_num = len(chunks) + 1
                if chunk_num > 1 and heading:
                    heading = f"{heading} (cont. {chunk_num})"

                chunks.append(
                    {
                        "file_path": rel_path,
                        "heading": heading,
                        "heading_level": section["heading_level"],
                        "line_start": current_start + 1,  # 1-based
                        "line_end": start_idx + i + 1,
                        "word_count": actual_words,
                        "content": chunk_text,
                        "layer": layer,
                        "sublayer": sublayer,
                        "origin": file_meta["origin"],
                        "status": file_meta["status"],
                        "date": date,
                        "file_size": file_size,
                    }
                )

            current_chunk_lines = []
            current_start = start_idx + i + 1
            word_count = 0

    return chunks


# --- Commands ---


def _index_files(conn: sqlite3.Connection, md_files: list[Path], repo_root: Path) -> tuple[int, int]:
    """Index a list of markdown files into the database. Returns (files, chunks)."""
    total_files = 0
    total_chunks = 0

    for md_file in md_files:
        chunks = chunk_file(md_file, repo_root)
        total_files += 1

        for chunk in chunks:
            conn.execute(
                """
                INSERT INTO chunks (
                    file_path, heading, heading_level,
                    line_start, line_end, word_count, content,
                    layer, sublayer, origin, status, date, file_size
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
                (
                    chunk["file_path"],
                    chunk["heading"],
                    chunk["heading_level"],
                    chunk["line_start"],
                    chunk["line_end"],
                    chunk["word_count"],
                    chunk["content"],
                    chunk["layer"],
                    chunk["sublayer"],
                    chunk["origin"],
                    chunk["status"],
                    chunk["date"],
                    chunk["file_size"],
                ),
            )
            total_chunks += 1

    return total_files, total_chunks


def _collect_corpus_files(repo_root: Path) -> list[Path]:
    """Collect all markdown files in content directories."""
    files = []
    for content_dir in CONTENT_DIRS:
        dir_path = repo_root / content_dir
        if not dir_path.exists():
            continue
        for md_file in sorted(dir_path.rglob("*.md")):
            if any(part.startswith((".", "_")) for part in md_file.parts):
                continue
            files.append(md_file)
    return files


def cmd_rebuild(args):
    """Full rebuild of the search index from markdown."""
    repo_root = find_repo_root()
    db_path = get_db_path(repo_root)
    db_path.parent.mkdir(parents=True, exist_ok=True)

    if getattr(args, "incremental", False) and db_path.exists():
        _cmd_rebuild_incremental(repo_root, db_path)
        return

    conn = sqlite3.connect(str(db_path))
    create_schema(conn)

    md_files = _collect_corpus_files(repo_root)
    total_files, total_chunks = _index_files(conn, md_files, repo_root)

    # Populate FTS index
    conn.execute(
        """
        INSERT INTO chunks_fts (rowid, heading, content, file_path)
        SELECT chunk_id, COALESCE(heading, ''), content, file_path
        FROM chunks
    """
    )

    # Record rebuild timestamp
    conn.execute(
        "INSERT OR REPLACE INTO rebuild_meta (key, value) VALUES ('rebuilt_at', ?)",
        (datetime.now().isoformat(),),
    )

    conn.commit()
    conn.close()

    print(f"Rebuilt {db_path.relative_to(repo_root)}")
    print(f"  {total_files} files, {total_chunks} chunks")


def _cmd_rebuild_incremental(repo_root: Path, db_path: Path):
    """Incremental rebuild: only re-index files modified since last rebuild."""
    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    # Get rebuild timestamp
    meta_row = conn.execute(
        "SELECT value FROM rebuild_meta WHERE key = 'rebuilt_at'"
    ).fetchone()

    if not meta_row:
        conn.close()
        print("No rebuild timestamp found. Running full rebuild.")
        conn2 = sqlite3.connect(str(db_path))
        create_schema(conn2)
        md_files = _collect_corpus_files(repo_root)
        total_files, total_chunks = _index_files(conn2, md_files, repo_root)
        conn2.execute(
            """
            INSERT INTO chunks_fts (rowid, heading, content, file_path)
            SELECT chunk_id, COALESCE(heading, ''), content, file_path
            FROM chunks
        """
        )
        conn2.execute(
            "INSERT OR REPLACE INTO rebuild_meta (key, value) VALUES ('rebuilt_at', ?)",
            (datetime.now().isoformat(),),
        )
        conn2.commit()
        conn2.close()
        print(f"Rebuilt {db_path.relative_to(repo_root)}")
        print(f"  {total_files} files, {total_chunks} chunks")
        return

    rebuild_time = datetime.fromisoformat(meta_row["value"])

    # Get indexed file paths from DB
    indexed_paths = set(
        r["file_path"]
        for r in conn.execute("SELECT DISTINCT file_path FROM chunks").fetchall()
    )

    # Collect current corpus
    corpus_files = _collect_corpus_files(repo_root)
    corpus_paths = {str(f.relative_to(repo_root)) for f in corpus_files}

    # Find files to update
    stale_files = []
    new_files = []
    for md_file in corpus_files:
        rel = str(md_file.relative_to(repo_root))
        mtime = datetime.fromtimestamp(md_file.stat().st_mtime)
        if rel not in indexed_paths:
            new_files.append(md_file)
        elif mtime > rebuild_time:
            stale_files.append(md_file)

    # Find deleted files (in DB but not on disk)
    deleted_paths = indexed_paths - corpus_paths

    if not stale_files and not new_files and not deleted_paths:
        conn.close()
        print("Index is current. No files to update.")
        return

    # Remove chunks for stale/deleted files
    paths_to_remove = {str(f.relative_to(repo_root)) for f in stale_files} | deleted_paths
    for path in paths_to_remove:
        # Remove from FTS first (content sync)
        chunk_ids = [
            r["chunk_id"]
            for r in conn.execute(
                "SELECT chunk_id FROM chunks WHERE file_path = ?", (path,)
            ).fetchall()
        ]
        for cid in chunk_ids:
            conn.execute(
                "INSERT INTO chunks_fts (chunks_fts, rowid, heading, content, file_path) "
                "VALUES ('delete', ?, "
                "(SELECT COALESCE(heading, '') FROM chunks WHERE chunk_id = ?), "
                "(SELECT content FROM chunks WHERE chunk_id = ?), "
                "(SELECT file_path FROM chunks WHERE chunk_id = ?))",
                (cid, cid, cid, cid),
            )
        conn.execute("DELETE FROM chunks WHERE file_path = ?", (path,))

    # Re-index stale and new files
    files_to_index = stale_files + new_files
    reindexed, new_chunks = _index_files(conn, files_to_index, repo_root)

    # Update FTS for new chunks (guard against empty IN clause)
    if files_to_index:
        conn.execute(
            """
            INSERT INTO chunks_fts (rowid, heading, content, file_path)
            SELECT chunk_id, COALESCE(heading, ''), content, file_path
            FROM chunks
            WHERE file_path IN ({})
        """.format(",".join("?" for _ in files_to_index)),
            [str(f.relative_to(repo_root)) for f in files_to_index],
        )

    # Update rebuild timestamp
    conn.execute(
        "INSERT OR REPLACE INTO rebuild_meta (key, value) VALUES ('rebuilt_at', ?)",
        (datetime.now().isoformat(),),
    )

    conn.commit()
    conn.close()

    print(f"Incremental rebuild of {db_path.relative_to(repo_root)}")
    print(f"  Updated: {len(stale_files)} stale, {len(new_files)} new, {len(deleted_paths)} deleted")
    print(f"  Re-indexed: {reindexed} files, {new_chunks} chunks")


def cmd_search(args):
    """Search the FTS index."""
    repo_root = find_repo_root()
    db_path = get_db_path(repo_root)

    if not db_path.exists():
        print(
            f"Database not found at {db_path.relative_to(repo_root)}. "
            "Run 'uv run scripts/kb_search.py rebuild' first.",
            file=sys.stderr,
        )
        sys.exit(2)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    query = args.query
    limit = args.top

    # Build the FTS5 query
    # Escape special FTS5 characters
    fts_query = re.sub(r'[^\w\s]', ' ', query).strip()
    if not fts_query:
        print("Empty query after sanitization.", file=sys.stderr)
        sys.exit(1)

    # Build WHERE clause for layer filter
    where_clause = ""
    params: list = []
    if args.layer:
        where_clause = "AND c.layer = ?"
        params.append(args.layer)

    # Search with BM25 ranking
    sql = f"""
        SELECT
            c.chunk_id,
            c.file_path,
            c.heading,
            c.heading_level,
            c.line_start,
            c.line_end,
            c.word_count,
            c.layer,
            c.sublayer,
            c.origin,
            c.status,
            c.date,
            c.file_size,
            rank
        FROM chunks_fts
        JOIN chunks c ON chunks_fts.rowid = c.chunk_id
        WHERE chunks_fts MATCH ?
        {where_clause}
        ORDER BY rank
        LIMIT ?
    """

    try:
        rows = conn.execute(sql, [fts_query] + params + [limit]).fetchall()
    except sqlite3.OperationalError as e:
        if "fts5" in str(e).lower():
            print(f"FTS5 query error: {e}", file=sys.stderr)
            sys.exit(1)
        raise

    if not rows:
        print(f'No results for "{query}".')
        conn.close()
        sys.exit(1)

    # Apply custom ranking adjustments
    scored_rows = []
    now = datetime.now()
    query_terms_lower = set(fts_query.lower().split())

    for row in rows:
        base_score = -row["rank"]  # FTS5 rank is negative (lower = better)

        # Heading match boost
        heading_boost = 0.0
        if row["heading"]:
            heading_lower = row["heading"].lower()
            if any(term in heading_lower for term in query_terms_lower):
                heading_boost = 0.3

        # Layer boost
        layer_boost = 0.0
        if args.layer:
            if row["layer"] == args.layer:
                layer_boost = 0.5
        else:
            # Default: slightly prefer meta
            if row["layer"] == "meta":
                layer_boost = 0.2

        # Recency boost
        recency_boost = 0.0
        if row["date"]:
            try:
                file_date = datetime.strptime(row["date"], "%Y-%m-%d")
                if (now - file_date) < timedelta(days=30):
                    recency_boost = 0.1
            except ValueError:
                pass

        final_score = base_score + heading_boost + layer_boost + recency_boost
        scored_rows.append((final_score, row))

    # Sort by final score (descending)
    scored_rows.sort(key=lambda x: x[0], reverse=True)

    # Output
    print(f'Found {len(scored_rows)} results for "{query}":')
    print()

    for i, (score, row) in enumerate(scored_rows, 1):
        section_info = ""
        if row["heading"]:
            section_info = f'Section: "{row["heading"]}" '
        section_info += f'(lines {row["line_start"]}-{row["line_end"]}, {row["word_count"]} words)'

        origin_info = row["origin"] or "unknown"
        status_info = row["status"] or "unknown"

        print(f'{i}. [{score:.2f}] {row["file_path"]} (chunk #{row["chunk_id"]})')
        print(f"   {section_info}")
        print(f"   Origin: {origin_info} | Status: {status_info}")
        if i < len(scored_rows):
            print()

    conn.close()


def cmd_read(args):
    """Read a specific chunk by ID."""
    repo_root = find_repo_root()
    db_path = get_db_path(repo_root)

    if not db_path.exists():
        print(
            f"Database not found. Run 'uv run scripts/kb_search.py rebuild' first.",
            file=sys.stderr,
        )
        sys.exit(2)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    row = conn.execute(
        "SELECT * FROM chunks WHERE chunk_id = ?", (args.chunk_id,)
    ).fetchone()

    if not row:
        print(f"Chunk {args.chunk_id} not found.", file=sys.stderr)
        conn.close()
        sys.exit(1)

    heading_display = row["heading"] or "(preamble)"
    origin_display = row["origin"] or "unknown"
    status_display = row["status"] or "unknown"
    date_display = row["date"] or "unknown"

    print(f"--- Chunk #{row['chunk_id']} ---")
    print(f"File: {row['file_path']}")
    print(
        f"Section: {heading_display} (lines {row['line_start']}-{row['line_end']})"
    )
    print(f"Origin: {origin_display} | Status: {status_display} | Date: {date_display}")
    print(f"Words: {row['word_count']}")
    print("---")
    print()
    print(row["content"])

    conn.close()


def cmd_status(args):
    """Show database status and staleness info."""
    repo_root = find_repo_root()
    db_path = get_db_path(repo_root)

    if not db_path.exists():
        print("KB Index Status")
        print(f"  Database: {DB_REL_PATH}")
        print("  Status: NOT BUILT")
        print("  Run: uv run scripts/kb_search.py rebuild")
        sys.exit(2)

    conn = sqlite3.connect(str(db_path))
    conn.row_factory = sqlite3.Row

    # Get rebuild timestamp
    meta_row = conn.execute(
        "SELECT value FROM rebuild_meta WHERE key = 'rebuilt_at'"
    ).fetchone()
    rebuilt_at = meta_row["value"] if meta_row else "unknown"

    # Get chunk stats
    total_chunks = conn.execute("SELECT COUNT(*) as n FROM chunks").fetchone()["n"]
    total_files = conn.execute(
        "SELECT COUNT(DISTINCT file_path) as n FROM chunks"
    ).fetchone()["n"]

    # Layer breakdown
    layer_rows = conn.execute(
        "SELECT layer, COUNT(DISTINCT file_path) as n FROM chunks GROUP BY layer ORDER BY layer"
    ).fetchall()
    layer_summary = ", ".join(f"{r['layer']}={r['n']}" for r in layer_rows)

    conn.close()

    # Check for stale files
    stale_files = []
    if rebuilt_at != "unknown":
        try:
            rebuild_time = datetime.fromisoformat(rebuilt_at)
            for content_dir in CONTENT_DIRS:
                dir_path = repo_root / content_dir
                if not dir_path.exists():
                    continue
                for md_file in dir_path.rglob("*.md"):
                    if any(part.startswith((".", "_")) for part in md_file.parts):
                        continue
                    mtime = datetime.fromtimestamp(md_file.stat().st_mtime)
                    if mtime > rebuild_time:
                        stale_files.append(
                            str(md_file.relative_to(repo_root))
                        )
        except (ValueError, OSError):
            pass

    print("KB Index Status")
    print(f"  Database: {DB_REL_PATH}")
    print(f"  Last rebuilt: {rebuilt_at}")
    print(f"  Total chunks: {total_chunks:,}")
    print(f"  Total files: {total_files}")
    print(f"  Files by layer: {layer_summary}")

    if stale_files:
        print(f"  Stale files: {len(stale_files)} (modified since last rebuild)")
        for sf in stale_files[:10]:
            print(f"    - {sf}")
        if len(stale_files) > 10:
            print(f"    ... and {len(stale_files) - 10} more")
    else:
        print("  Stale files: 0 (index is current)")


# --- Main ---


def main():
    parser = argparse.ArgumentParser(
        description="Fermi KB full-text search CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """\
            Examples:
              uv run scripts/kb_search.py rebuild
              uv run scripts/kb_search.py search "dose response model"
              uv run scripts/kb_search.py search "coherence engine" --layer meta
              uv run scripts/kb_search.py read 42
              uv run scripts/kb_search.py status
        """
        ),
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # rebuild
    rebuild_parser = subparsers.add_parser("rebuild", help="Rebuild the search index from markdown")
    rebuild_parser.add_argument(
        "--incremental", action="store_true",
        help="Only re-index files modified since last rebuild"
    )

    # search
    search_parser = subparsers.add_parser("search", help="Search the knowledge base")
    search_parser.add_argument("query", help="Search query")
    search_parser.add_argument(
        "--layer",
        choices=["examples", "raw", "meta", "special_projects", "views"],
        help="Filter results to a specific layer",
    )
    search_parser.add_argument(
        "--top", type=int, default=10, help="Maximum results (default: 10)"
    )

    # read
    read_parser = subparsers.add_parser("read", help="Read a specific chunk by ID")
    read_parser.add_argument("chunk_id", type=int, help="Chunk ID from search results")

    # status
    subparsers.add_parser("status", help="Show database status and staleness")

    args = parser.parse_args()

    if args.command == "rebuild":
        cmd_rebuild(args)
    elif args.command == "search":
        cmd_search(args)
    elif args.command == "read":
        cmd_read(args)
    elif args.command == "status":
        cmd_status(args)


if __name__ == "__main__":
    main()
