#!/bin/bash
#
# kb_maintenance.sh — one-shot KB maintenance sequence
#
# Runs the standard drift-reconciliation pipeline:
#   1. Regenerate index/router.md
#   2. Incremental rebuild of search index
#   3. Verify no stale files remain (loud warning if any)
#   4. Run structural audit at ERROR severity
#
# Exit code: 0 if all clean, non-zero if audit errors found or search
# index still reports stale after rebuild. Intended for ad-hoc use
# between sessions or in CI-like checks. The session checkpoint skill
# (goodbye-fermi) runs an equivalent sequence inline.

set -u

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

FAIL=0

echo "=== KB Maintenance ==="
echo ""

# 1. Router
echo "→ Regenerating router..."
if uv run scripts/generate_router.py 2>&1 | sed 's/^/  /'; then
    echo "  ✓ Router updated"
else
    echo "  ✗ Router generation failed"
    FAIL=1
fi
echo ""

# 2. Search index rebuild
echo "→ Rebuilding search index (incremental)..."
if uv run scripts/kb_search.py rebuild --incremental 2>&1 | sed 's/^/  /'; then
    echo "  ✓ Search index rebuilt"
else
    echo "  ✗ Search index rebuild failed"
    FAIL=1
fi
echo ""

# 3. Stale-check after rebuild
echo "→ Verifying index is current..."
STATUS_OUT=$(uv run scripts/kb_search.py status 2>/dev/null || echo "")
STALE_LINE=$(echo "$STATUS_OUT" | grep -o 'Stale files: [0-9]*' | head -1)
STALE_COUNT=$(echo "$STALE_LINE" | grep -o '[0-9]*')
if [ -z "$STALE_COUNT" ]; then
    echo "  ⚠ Could not parse stale count from kb_search status"
    FAIL=1
elif [ "$STALE_COUNT" != "0" ]; then
    echo "  ✗ $STALE_COUNT stale file(s) AFTER incremental rebuild."
    echo "    Try full rebuild: uv run scripts/kb_search.py rebuild"
    FAIL=1
else
    echo "  ✓ No stale files"
fi
echo ""

# 4. Audit
echo "→ Running audit (ERROR severity)..."
AUDIT_OUT=$(uv run scripts/kb_audit.py --severity ERROR 2>&1)
AUDIT_COUNT=$(echo "$AUDIT_OUT" | grep "ERRORs:" | grep -o '[0-9]*' | head -1)
if [ -z "$AUDIT_COUNT" ] || [ "$AUDIT_COUNT" = "0" ]; then
    echo "  ✓ No audit errors"
else
    echo "  ✗ $AUDIT_COUNT audit ERROR(s):"
    echo "$AUDIT_OUT" | grep "^- " | sed 's/^/    /'
    FAIL=1
fi
echo ""

if [ "$FAIL" = "0" ]; then
    echo "=== KB Maintenance: clean ==="
    exit 0
else
    echo "=== KB Maintenance: issues found (see above) ==="
    exit 1
fi
