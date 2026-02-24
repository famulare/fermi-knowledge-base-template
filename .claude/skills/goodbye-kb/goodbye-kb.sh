#!/bin/bash

# Knowledge Base Session Checkpoint
# Runs at end of session to review, commit, and push KB changes

set -e

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
cd "$REPO_ROOT"

echo "=== KB Session Checkpoint ==="
echo ""

# Learning review
echo "=== Learning Artifact Review ==="
echo "Review: Did this session reveal patterns in connection surfacing?"
echo "Update learning/connection_feedback.md only if:"
echo "  - New connection patterns emerged (useful or unhelpful)"
echo "  - Suppression rules should be refined"
echo "  - Confidence levels shifted based on feedback"
echo ""
echo "It's fine if no learning updates are warranted."
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

# Check for learning updates
LEARNING_COUNT=$(git status --short learning/ 2>/dev/null | wc -l | tr -d ' ')
if [ "$LEARNING_COUNT" -gt 0 ]; then
    echo "Learning updates:"
    git status --short learning/ | sed 's/^/  /'
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

# Stage and commit if there are changes
if ! git diff --quiet raw/ meta/ index/ learning/ views/persistent/ 2>/dev/null || \
   [ -n "$(git status --short raw/ meta/ index/ learning/ views/persistent/ 2>/dev/null)" ]; then

    echo "Committing KB changes..."
    git add raw/ meta/ index/ learning/ views/persistent/ 2>/dev/null || true

    if ! git diff-index --quiet --cached HEAD 2>/dev/null; then
        # Generate commit message
        COMMIT_MSG="KB session checkpoint

Captured knowledge and learning updates from session.

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
        if [ "$LEARNING_COUNT" -gt 0 ]; then
            COMMIT_MSG="${COMMIT_MSG}- Learning updates: $LEARNING_COUNT file(s)
"
        fi

        git commit -m "$COMMIT_MSG"
        echo "✓ Changes committed"
    fi
else
    echo "No KB changes to commit this session"
fi

echo ""

# Push to remote (default on)
echo "Pushing to remote..."
if git push 2>/dev/null; then
    echo "✓ Pushed to remote"
else
    echo "⚠ Push failed (remote may not be configured or reachable)"
fi

echo ""
echo "=== Session Complete ==="
echo "Knowledge base state preserved."
echo ""
