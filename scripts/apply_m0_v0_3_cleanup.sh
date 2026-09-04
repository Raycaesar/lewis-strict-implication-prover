#!/usr/bin/env bash
set -euo pipefail

echo "Applying M0.3 repository cleanup..."

# Archive the superseded active foundational spec if present.
if [ -f docs/FOUNDATIONAL_SPEC_v0.2.md ]; then
  mkdir -p docs/archive
  if [ ! -f docs/archive/FOUNDATIONAL_SPEC_v0.2.md ]; then
    mv docs/FOUNDATIONAL_SPEC_v0.2.md docs/archive/FOUNDATIONAL_SPEC_v0.2.md
  else
    rm docs/FOUNDATIONAL_SPEC_v0.2.md
  fi
fi

# Remove Windows Mark-of-the-Web metadata materialized as ordinary files.
find . \
  -path './.git' -prune -o \
  -type f -name '*:Zone.Identifier' -print -delete

echo
echo "Tracked Zone.Identifier files remaining:"
git ls-files '*:Zone.Identifier' || true

echo
echo "If names are printed above, stage their deletion with:"
echo "  git add -A"
echo
echo "Cleanup complete."
