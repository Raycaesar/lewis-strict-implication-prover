#!/usr/bin/env bash
set -euo pipefail

echo "Removing materialized Windows Zone.Identifier metadata files..."
find . \
  -path './.git' -prune -o \
  -type f -name '*:Zone.Identifier' -print -delete

echo
echo "Done."
echo "Review with: git status --short"
