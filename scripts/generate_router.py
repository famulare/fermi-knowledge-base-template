#!/usr/bin/env python3
"""Generate index/router.md from the markdown corpus.

This script walks the KB, extracts structure from each file, groups files
by domain (using index/tags.md as the clustering source), and generates
a compact router document suitable for always-loaded context.

The router is fully generated — no hand edits. If editorial curation is
needed, it goes in a separate seed file that this generator consumes.

Usage:
    uv run scripts/generate_router.py
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path


# Directories to walk for content files
CONTENT_DIRS = [
    "examples",
    "raw",
    "meta",
    "special_projects",
    "views/persistent",
]

# Threshold for "large file" section inventories (bytes)
LARGE_FILE_THRESHOLD = 20_000

# Maximum number of large files to include section inventories for
MAX_SECTION_INVENTORIES = 15

# How many recent ingests to include in the router
RECENT_INGEST_COUNT = 5

# Domain consolidation: tags are grouped into higher-level domains.
# A file is assigned to the domain of its first matching tag; tags not
# mapped become their own domain (title-cased fallback).
#
# The mapping and ordering are read from config/system.yml (the `domains`
# block) so each user defines their own. The neutral defaults below are used
# only when that block is absent or pyyaml is unavailable.
_DEFAULT_TAG_TO_DOMAIN = {
    "immunology": "Immunology & Dose-Response",
    "dose-response": "Immunology & Dose-Response",
    "infectious-disease": "Infectious Disease Modeling",
    "molecular-evolution": "Infectious Disease Modeling",
    "epidemiology": "Infectious Disease Modeling",
    "ai-cognition": "AI Cognition",
    "llm-phenomenology": "AI Cognition",
    "methodology": "Methodology & Scientific Philosophy",
    "modeling-philosophy": "Methodology & Scientific Philosophy",
    "scientific-integrity": "Methodology & Scientific Philosophy",
}

_DEFAULT_DOMAIN_ORDER = [
    "Infectious Disease Modeling",
    "Immunology & Dose-Response",
    "AI Cognition",
    "Methodology & Scientific Philosophy",
]

_domains_cache: tuple[dict, list] | None = None


def get_domains(repo_root: Path) -> tuple[dict, list]:
    """Return (tag_to_domain, domain_order) from config/system.yml, or neutral defaults.

    Reads the `domains` block of config/system.yml. Falls back to the neutral
    defaults above if the file/block is absent or pyyaml is unavailable.
    """
    global _domains_cache
    if _domains_cache is not None:
        return _domains_cache
    tag_map: dict = {}
    order: list = []
    config_file = repo_root / "config" / "system.yml"
    if config_file.exists():
        try:
            import yaml

            with open(config_file, encoding="utf-8") as f:
                data = yaml.safe_load(f) or {}
            block = data.get("domains", {}) or {}
            tag_map = block.get("tags_to_domains") or {}
            order = block.get("preferred_order") or []
        except Exception:
            tag_map, order = {}, []
    _domains_cache = (
        tag_map or _DEFAULT_TAG_TO_DOMAIN,
        order or _DEFAULT_DOMAIN_ORDER,
    )
    return _domains_cache


def find_repo_root() -> Path:
    """Find the repository root by looking for CLAUDE.md."""
    current = Path(__file__).resolve().parent
    while current != current.parent:
        if (current / "CLAUDE.md").exists():
            return current
        current = current.parent
    return Path(__file__).resolve().parent.parent


def extract_headings(filepath: Path) -> list[dict]:
    """Extract markdown headings with line numbers from a file."""
    headings = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            for line_num, line in enumerate(f, 1):
                m = re.match(r"^(#{1,4})\s+(.+)$", line.rstrip())
                if m:
                    headings.append(
                        {
                            "level": len(m.group(1)),
                            "text": m.group(2).strip(),
                            "line_num": line_num,
                        }
                    )
    except OSError:
        pass
    return headings


def extract_title(headings: list[dict], filepath: Path) -> str:
    """Get the title from the first H1, or fall back to filename."""
    for h in headings:
        if h["level"] == 1:
            return h["text"]
    return filepath.stem


def extract_date_from_filename(filepath: Path) -> str | None:
    """Extract YYYY-MM-DD date prefix from filename if present."""
    m = re.match(r"(\d{4}-\d{2}-\d{2})", filepath.name)
    return m.group(1) if m else None


def classify_layer(rel_path: str) -> tuple[str, str | None]:
    """Classify a file into layer and sublayer."""
    parts = rel_path.split("/")
    layer = parts[0]
    if layer == "views":
        return "views", None
    sublayer = parts[1] if len(parts) > 2 else None
    return layer, sublayer


def parse_tags_file(repo_root: Path) -> dict[str, list[str]]:
    """Parse index/tags.md to extract tag -> file list mappings."""
    tags_file = repo_root / "index" / "tags.md"
    if not tags_file.exists():
        return {}

    tags: dict[str, list[str]] = {}
    current_tag = None
    in_files = False

    with open(tags_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.rstrip()
            m = re.match(r"^### (\S+)$", line)
            if m:
                current_tag = m.group(1)
                tags[current_tag] = []
                in_files = False
                continue
            if current_tag:
                if line.startswith("**Files:**"):
                    in_files = True
                    continue
                if in_files:
                    fm = re.match(r"^- (.+\.md).*$", line)
                    if fm:
                        path = fm.group(1).strip()
                        path = re.split(r"\s+\(", path)[0].strip()
                        tags[current_tag].append(path)
                    elif line and not line.startswith("-") and not line.startswith(" "):
                        in_files = False

    return tags


def build_file_to_domain(tags: dict[str, list[str]], repo_root: Path) -> dict[str, str]:
    """Build file -> domain mapping. First matching tag wins."""
    tag_to_domain, _ = get_domains(repo_root)
    file_domain: dict[str, str] = {}
    for tag, files in tags.items():
        domain = tag_to_domain.get(tag, tag.replace("-", " ").title())
        for f in files:
            if f not in file_domain:
                file_domain[f] = domain
    return file_domain


def extract_first_sentence(filepath: Path, start_line: int) -> str:
    """Extract first non-empty content sentence after a given line."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()
        for i in range(start_line, min(start_line + 10, len(lines))):
            line = lines[i].strip()
            if not line or line.startswith("---") or line.startswith("**") or line.startswith("#"):
                continue
            if line.startswith("|") or line.startswith(">"):
                continue
            sentence = re.split(r"[.!?]", line)[0].strip()
            if len(sentence) > 10:
                if len(sentence) > 100:
                    sentence = sentence[:97] + "..."
                return sentence
        return ""
    except (OSError, IndexError):
        return ""


def build_section_inventory(filepath: Path, headings: list[dict]) -> list[dict]:
    """Build section inventory for a large file."""
    try:
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            total_lines = sum(1 for _ in f)
    except OSError:
        total_lines = 0

    # Use H2 headings primarily, H3 only if very few H2s
    h2s = [h for h in headings if h["level"] == 2]
    if len(h2s) >= 3:
        relevant = h2s
    else:
        relevant = [h for h in headings if h["level"] in (2, 3)]

    sections = []
    for i, h in enumerate(relevant):
        start = h["line_num"]
        end = relevant[i + 1]["line_num"] - 1 if i + 1 < len(relevant) else total_lines
        topic = extract_first_sentence(filepath, h["line_num"])
        sections.append(
            {"heading": h["text"], "lines": f"{start}-{end}", "topic": topic}
        )
    return sections


def parse_recent_ingests(repo_root: Path, count: int = 5) -> list[dict]:
    """Parse recent_ingests.md to extract the last N ingest entries."""
    ingests_file = repo_root / "views" / "persistent" / "recent_ingests.md"
    if not ingests_file.exists():
        return []
    entries = []
    with open(ingests_file, "r", encoding="utf-8") as f:
        for line in f:
            m = re.match(r"^### (\d{4}-\d{2}-\d{2}):\s+(.+)$", line.rstrip())
            if m:
                entries.append({"date": m.group(1), "title": m.group(2).strip()})
    return entries[:count]


def walk_content(repo_root: Path) -> list[dict]:
    """Walk content directories and extract file info."""
    files = []
    for content_dir in CONTENT_DIRS:
        dir_path = repo_root / content_dir
        if not dir_path.exists():
            continue
        for md_file in sorted(dir_path.rglob("*.md")):
            if any(part.startswith((".", "_")) for part in md_file.parts):
                continue
            if md_file.name == "README.md":
                continue
            rel_path = str(md_file.relative_to(repo_root))
            size = md_file.stat().st_size
            headings = extract_headings(md_file)
            title = extract_title(headings, md_file)
            date = extract_date_from_filename(md_file)
            layer, sublayer = classify_layer(rel_path)
            files.append(
                {
                    "path": md_file,
                    "rel_path": rel_path,
                    "size": size,
                    "title": title,
                    "date": date,
                    "layer": layer,
                    "sublayer": sublayer,
                    "headings": headings,
                    "is_large": size >= LARGE_FILE_THRESHOLD,
                }
            )
    return files


def pluralize_files(n: int) -> str:
    return "1 file" if n == 1 else f"{n} files"


def format_size(size_bytes: int) -> str:
    """Format file size for display."""
    if size_bytes >= 1_000_000:
        return f"{size_bytes / 1_000_000:.0f}MB"
    elif size_bytes >= 1_000:
        return f"{size_bytes / 1_000:.0f}KB"
    else:
        return f"{size_bytes}B"


def generate_router(repo_root: Path) -> str:
    """Generate the router markdown content."""
    files = walk_content(repo_root)
    tags = parse_tags_file(repo_root)
    file_to_domain = build_file_to_domain(tags, repo_root)
    recent = parse_recent_ingests(repo_root, RECENT_INGEST_COUNT)

    # Assign files to domains
    domains: dict[str, list[dict]] = {}
    for f in files:
        domain = file_to_domain.get(f["rel_path"], None)
        if domain is None:
            # Fallback: group by top-level directory
            layer = f["layer"]
            if layer == "special_projects":
                # Group by project name
                parts = f["rel_path"].split("/")
                if len(parts) >= 2:
                    domain = f"Special Project: {parts[1]}"
                else:
                    domain = "Special Projects"
            elif layer == "learning":
                domain = "Learning"
            else:
                domain = "Uncategorized"
        domains.setdefault(domain, []).append(f)

    # Collect large files for section inventories (top N by size)
    large_files = sorted(
        [f for f in files if f["is_large"]],
        key=lambda f: f["size"],
        reverse=True,
    )[:MAX_SECTION_INVENTORIES]

    now = datetime.now().strftime("%Y-%m-%d %H:%M")

    lines: list[str] = []
    lines.append("# KB Router")
    lines.append(
        f"**Generated:** {now} | **Files:** {len(files)} | "
        f"**Domains:** {len(domains)}"
    )
    lines.append("")
    lines.append(
        "> This file is fully generated by `scripts/generate_router.py`. "
        "Do not hand-edit."
    )
    lines.append(
        "> Source of truth: the markdown corpus. Regenerate after any ingest."
    )
    lines.append("")
    lines.append("---")
    lines.append("")

    # Recent activity
    if recent:
        lines.append("## Recent Activity")
        lines.append("")
        for entry in recent:
            lines.append(f"- **{entry['date']}:** {entry['title']}")
        lines.append("")
        lines.append("---")
        lines.append("")

    # Emit domains in preferred order, then alphabetical for the rest
    _, domain_order = get_domains(repo_root)
    ordered_domains = []
    for d in domain_order:
        if d in domains:
            ordered_domains.append(d)
    for d in sorted(domains.keys()):
        if d not in ordered_domains:
            ordered_domains.append(d)

    for domain_name in ordered_domains:
        domain_files = domains[domain_name]

        if domain_name == "Uncategorized":
            # Compress uncategorized into directory summary
            lines.append(
                f"## Uncategorized ({pluralize_files(len(domain_files))})"
            )
            lines.append("")
            lines.append(
                "Files reachable via search but not directly tagged. "
                "Breakdown by directory:"
            )
            lines.append("")
            dir_counts: dict[str, int] = {}
            dir_large: dict[str, list[str]] = {}
            for f in domain_files:
                # Group by layer/sublayer directory
                parts = f["rel_path"].split("/")
                if len(parts) >= 3:
                    dir_key = "/".join(parts[:2])
                else:
                    dir_key = parts[0]
                dir_counts[dir_key] = dir_counts.get(dir_key, 0) + 1
                if f["is_large"]:
                    dir_large.setdefault(dir_key, []).append(f["rel_path"])
            for dk in sorted(dir_counts.keys()):
                count = dir_counts[dk]
                large_note = ""
                if dk in dir_large:
                    large_paths = ", ".join(
                        f"`{p}`" for p in dir_large[dk]
                    )
                    large_note = f" — LARGE: {large_paths}"
                lines.append(f"- `{dk}/` ({pluralize_files(count)}){large_note}")
            lines.append("")
            continue

        lines.append(f"## {domain_name} ({pluralize_files(len(domain_files))})")
        lines.append("")

        # Sort by layer priority then path
        layer_priority = {"examples": 0, "meta": 1, "raw": 2, "special_projects": 3, "views": 4}
        domain_files.sort(
            key=lambda f: (layer_priority.get(f["layer"], 5), f["rel_path"])
        )

        for f in domain_files:
            size_str = format_size(f["size"])
            large_marker = ", LARGE" if f["is_large"] else ""
            title = f["title"]
            if len(title) > 80:
                title = title[:77] + "..."
            lines.append(f"- `{f['rel_path']}` ({size_str}{large_marker}) — {title}")

        lines.append("")

    # Large file section inventories
    lines.append("---")
    lines.append("")
    lines.append("## Large File Section Inventories")
    lines.append("")
    lines.append(
        "Files over 20KB with heading maps. **Use line ranges for targeted reads.**"
    )
    lines.append("")

    for f in large_files:
        sections = build_section_inventory(f["path"], f["headings"])
        size_str = format_size(f["size"])
        lines.append(f"### `{f['rel_path']}` ({size_str})")
        lines.append("")
        if sections:
            lines.append("| Section | Lines | Topic |")
            lines.append("|---------|-------|-------|")
            for s in sections:
                lines.append(f"| {s['heading']} | {s['lines']} | {s['topic']} |")
        else:
            lines.append(
                "*No heading structure — read in ~2000-line chunks.*"
            )
        lines.append("")

    return "\n".join(lines)


def validate_tags(repo_root: Path, corpus_paths: set[str]) -> str:
    """Validate and regenerate index/tags.md.

    Reads existing tags.md as seed (preserving editorial content: descriptions,
    types), validates file references against current corpus, removes stale
    references, and reports untagged files.

    Returns the regenerated tags.md content.
    """
    tags_file = repo_root / "index" / "tags.md"
    if not tags_file.exists():
        return ""

    # Directory entries in tags end with "/" — match any file under that dir
    def path_exists_in_corpus(ref: str) -> bool:
        if ref.endswith("/"):
            prefix = ref.rstrip("/")
            return any(p.startswith(prefix + "/") or p == prefix for p in corpus_paths)
        return ref in corpus_paths

    with open(tags_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Parse tag entries
    lines = content.split("\n")
    output_lines: list[str] = []
    tagged_files: set[str] = set()
    stale_count = 0
    in_active_tags = False
    in_files_section = False

    i = 0
    while i < len(lines):
        line = lines[i]

        # Detect start of Active Tags section
        if line.strip() == "## Active Tags":
            in_active_tags = True
            output_lines.append(line)
            i += 1
            continue

        # Before Active Tags or after it ends — pass through
        if not in_active_tags:
            output_lines.append(line)
            i += 1
            continue

        # Detect end of Active Tags (next ## section)
        if line.startswith("## ") and line.strip() != "## Active Tags":
            in_active_tags = False
            output_lines.append(line)
            i += 1
            continue

        # Inside Active Tags: process tag entries
        if line.startswith("### "):
            in_files_section = False
            output_lines.append(line)
            i += 1
            continue

        if line.startswith("**Files:**"):
            in_files_section = True
            output_lines.append(line)
            i += 1
            continue

        if in_files_section:
            fm = re.match(r"^- (.+)$", line)
            if fm:
                ref = fm.group(1).strip()
                # Strip trailing annotations like "(all files)" or "(co-author)"
                ref_path = re.split(r"\s+\(", ref)[0].strip()
                if path_exists_in_corpus(ref_path):
                    tagged_files.add(ref_path)
                    output_lines.append(line)
                else:
                    stale_count += 1
                    # Skip this stale reference
                i += 1
                continue
            else:
                # Non-file line ends the files section
                in_files_section = False
                output_lines.append(line)
                i += 1
                continue

        output_lines.append(line)
        i += 1

    # Update timestamp
    today = datetime.now().strftime("%Y-%m-%d")
    result = "\n".join(output_lines)
    result = re.sub(
        r"\*\*Last updated:\*\* \d{4}-\d{2}-\d{2}",
        f"**Last updated:** {today}",
        result,
    )

    # Report untagged files
    untagged = sorted(corpus_paths - tagged_files)
    # Filter to only meta/ files (raw files being untagged is normal)
    untagged_meta = [p for p in untagged if p.startswith("meta/")]

    print(f"  Tags: {stale_count} stale references removed")
    if untagged_meta:
        print(f"  Untagged meta files: {len(untagged_meta)}")
        for p in untagged_meta[:10]:
            print(f"    - {p}")
        if len(untagged_meta) > 10:
            print(f"    ... and {len(untagged_meta) - 10} more")

    return result


def validate_entities(repo_root: Path, corpus_paths: set[str]) -> str:
    """Validate and regenerate index/entities.md.

    Reads existing entities.md as seed (preserving editorial content: aliases,
    types, notes), validates occurrence references against current corpus,
    removes stale references.

    Returns the regenerated entities.md content.
    """
    entities_file = repo_root / "index" / "entities.md"
    if not entities_file.exists():
        return ""

    # Known layer prefixes that indicate a file path reference
    LAYER_PREFIXES = ("meta/", "raw/", "special_projects/", "views/", "index/", "contracts/")

    def path_exists_in_corpus(ref: str) -> bool:
        if ref.endswith("/"):
            prefix = ref.rstrip("/")
            return any(p.startswith(prefix + "/") or p == prefix for p in corpus_paths)
        return ref in corpus_paths

    def is_file_path_reference(ref: str) -> bool:
        """Check if a reference looks like a file path (vs free-form text)."""
        return any(ref.startswith(prefix) for prefix in LAYER_PREFIXES)

    with open(entities_file, "r", encoding="utf-8") as f:
        content = f.read()

    lines = content.split("\n")
    output_lines: list[str] = []
    stale_count = 0
    in_occurrences = False

    for line in lines:
        if line.startswith("**Occurrences:**"):
            in_occurrences = True
            output_lines.append(line)
            continue

        if in_occurrences:
            fm = re.match(r"^- (.+)$", line)
            if fm:
                ref = fm.group(1).strip()
                # Extract path before any trailing annotation like "(co-author)"
                ref_path = re.split(r"\s+\(", ref)[0].strip()
                if is_file_path_reference(ref_path):
                    # This is a file path — validate it
                    if path_exists_in_corpus(ref_path):
                        output_lines.append(line)
                    else:
                        stale_count += 1
                else:
                    # Free-form text reference — preserve as-is
                    output_lines.append(line)
                continue
            else:
                # Non-list line ends occurrences section
                in_occurrences = False
                output_lines.append(line)
                continue

        output_lines.append(line)

    # Update timestamp
    today = datetime.now().strftime("%Y-%m-%d")
    result = "\n".join(output_lines)
    result = re.sub(
        r"\*\*Last updated:\*\* \d{4}-\d{2}-\d{2}",
        f"**Last updated:** {today}",
        result,
    )

    print(f"  Entities: {stale_count} stale references removed")
    return result


def main():
    import argparse as _argparse

    parser = _argparse.ArgumentParser(
        description="Generate index/router.md from the markdown corpus"
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Also validate and regenerate index/tags.md and index/entities.md",
    )
    args = parser.parse_args()

    repo_root = find_repo_root()
    router_content = generate_router(repo_root)

    output_path = repo_root / "index" / "router.md"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(router_content)

    line_count = router_content.count("\n") + 1
    byte_count = len(router_content.encode("utf-8"))
    large_count = router_content.count(", LARGE)")
    print(f"Generated {output_path.relative_to(repo_root)}")
    print(f"  {line_count} lines, {format_size(byte_count)}")
    print(f"  {large_count} large file markers, {MAX_SECTION_INVENTORIES} section inventories")

    if args.full:
        # Collect all corpus file paths for validation
        files = walk_content(repo_root)
        corpus_paths = {f["rel_path"] for f in files}

        print()
        print("Validating index files (--full):")

        tags_content = validate_tags(repo_root, corpus_paths)
        if tags_content:
            tags_path = repo_root / "index" / "tags.md"
            with open(tags_path, "w", encoding="utf-8") as f:
                f.write(tags_content)
            print(f"  Updated {tags_path.relative_to(repo_root)}")

        entities_content = validate_entities(repo_root, corpus_paths)
        if entities_content:
            entities_path = repo_root / "index" / "entities.md"
            with open(entities_path, "w", encoding="utf-8") as f:
                f.write(entities_content)
            print(f"  Updated {entities_path.relative_to(repo_root)}")


if __name__ == "__main__":
    main()
