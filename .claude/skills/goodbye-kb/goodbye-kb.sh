#!/bin/bash

# Knowledge Base Session Checkpoint
# Runs at end of session to review KB state, run maintenance, and commit changes.
# Pushing to a remote is optional and off by default (pass --push to enable).

set -e

PUSH=0
for arg in "$@"; do
    case "$arg" in
        --push) PUSH=1 ;;
    esac
done

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

# Content directories tracked by the checkpoint. Edit this list if your KB
# grows new top-level content dirs.
CONTENT_DIRS="raw meta index views/persistent special_projects contracts examples"

echo "=== KB Session Checkpoint ==="
echo ""

# KB State Summary
echo "=== KB State This Session ==="

# Check for new raw ingests
RAW_COUNT=$(git status --short raw/ 2>/dev/null | wc -l | tr -d ' ')
if [ "$RAW_COUNT" -gt 0 ]; then
    echo "Raw ingests:"
    git status --short raw/ | sed 's/^/  /'
    echo ""
fi

# Check for new meta entries
META_COUNT=$(git status --short meta/ 2>/dev/null | wc -l | tr -d ' ')
if [ "$META_COUNT" -gt 0 ]; then
    echo "Meta entries:"
    git status --short meta/ | sed 's/^/  /'
    echo ""
fi

# Check for index updates
INDEX_COUNT=$(git status --short index/ 2>/dev/null | wc -l | tr -d ' ')
if [ "$INDEX_COUNT" -gt 0 ]; then
    echo "Index updates:"
    git status --short index/ | sed 's/^/  /'
    echo ""
fi

# Check for view updates
VIEWS_COUNT=$(git status --short views/persistent/ 2>/dev/null | wc -l | tr -d ' ')
if [ "$VIEWS_COUNT" -gt 0 ]; then
    echo "View updates:"
    git status --short views/persistent/ | sed 's/^/  /'
    echo ""
fi

# Show recent ingests summary if file exists
if [ -f views/persistent/recent_ingests.md ]; then
    echo "Recent activity (last 3 entries):"
    grep "^### " views/persistent/recent_ingests.md | head -3 | sed 's/^### /  • /'
    echo ""
fi

# Regenerate router and refresh search index before commit
# Router goes into the commit; DB is gitignored but stays fresh for next session
if [ -f scripts/generate_router.py ]; then
    echo "Regenerating router..."
    uv run scripts/generate_router.py 2>/dev/null && echo "✓ Router updated" || echo "⚠ Router generation failed"
    echo ""
fi

if [ -f scripts/kb_search.py ]; then
    echo "Refreshing search index..."
    if uv run scripts/kb_search.py rebuild --incremental 2>/dev/null; then
        echo "✓ Search index updated"
        # Verify no stale files remain post-rebuild. If rebuild reports stale,
        # the index has drifted (e.g. files modified during rebuild, or script bug).
        # Surface loudly — silent drift defeats the retrieval gate.
        STATUS_OUT=$(uv run scripts/kb_search.py status 2>/dev/null || echo "")
        STALE_LINE=$(echo "$STATUS_OUT" | grep -o 'Stale files: [0-9]*' | head -1)
        STALE_COUNT=$(echo "$STALE_LINE" | grep -o '[0-9]*')
        if [ -n "$STALE_COUNT" ] && [ "$STALE_COUNT" != "0" ]; then
            echo "⚠ WARNING: kb_search status reports $STALE_COUNT stale file(s) AFTER rebuild."
            echo "  The incremental rebuild did not fully reconcile. Investigate:"
            echo "    uv run scripts/kb_search.py status"
            echo "  Consider a full rebuild: uv run scripts/kb_search.py rebuild"
        fi
    else
        echo "⚠ Search index refresh failed"
    fi
    echo ""
fi

# Validate KB integrity (cross-references, structural compliance)
if [ -f scripts/kb_audit.py ]; then
    echo "Running KB audit (ERROR-level checks)..."
    AUDIT_ERRORS=$(uv run scripts/kb_audit.py --severity ERROR 2>/dev/null | grep "ERRORs:" | grep -o '[0-9]*')
    if [ "$AUDIT_ERRORS" = "0" ] || [ -z "$AUDIT_ERRORS" ]; then
        echo "✓ No audit errors"
    else
        echo "⚠ $AUDIT_ERRORS audit ERROR(s) found — review before committing:"
        uv run scripts/kb_audit.py --severity ERROR 2>/dev/null | grep "^- "
    fi
    echo ""
fi

# Stage and commit if there are changes
if ! git diff --quiet $CONTENT_DIRS 2>/dev/null || \
   [ -n "$(git status --short $CONTENT_DIRS 2>/dev/null)" ]; then

    echo "Committing KB changes..."
    git add $CONTENT_DIRS 2>/dev/null || true

    if ! git diff-index --quiet --cached HEAD 2>/dev/null; then
        # Generate commit message
        COMMIT_MSG="KB session checkpoint

Captured knowledge updates from session.

"

        # Add details based on what changed
        if [ "$RAW_COUNT" -gt 0 ]; then
            COMMIT_MSG="${COMMIT_MSG}- Raw ingests: $RAW_COUNT file(s)
"
        fi
        if [ "$META_COUNT" -gt 0 ]; then
            COMMIT_MSG="${COMMIT_MSG}- Meta entries: $META_COUNT file(s)
"
        fi
        if [ "$INDEX_COUNT" -gt 0 ]; then
            COMMIT_MSG="${COMMIT_MSG}- Index updates: $INDEX_COUNT file(s)
"
        fi

        git commit -m "$COMMIT_MSG"
        echo "✓ Changes committed"
    fi
else
    echo "No KB changes to commit this session"
fi

echo ""

# Push to remote (optional, off by default). Enable with: goodbye-kb.sh --push
if [ "$PUSH" -eq 1 ]; then
    echo "Pushing to remote..."
    if git push 2>/dev/null; then
        echo "✓ Pushed to remote"
    else
        echo "⚠ Push failed (remote may not be configured or reachable)"
    fi
    echo ""
else
    echo "Skipping push (run with --push to push to a remote)."
    echo ""
fi

echo "=== Session Complete ==="
echo "Knowledge base state preserved."
echo ""
