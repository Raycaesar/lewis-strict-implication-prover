#!/usr/bin/env bash
set -euo pipefail

echo "Applying M0.6 repository cleanup..."

mkdir -p docs/archive audit/m0/archive

if [ -f docs/FOUNDATIONAL_SPEC_v0.5.md ]; then
  if [ ! -f docs/archive/FOUNDATIONAL_SPEC_v0.5.md ]; then
    mv docs/FOUNDATIONAL_SPEC_v0.5.md docs/archive/FOUNDATIONAL_SPEC_v0.5.md
  else
    rm -f docs/FOUNDATIONAL_SPEC_v0.5.md
  fi
fi

if [ -f audit/m0/WORK_MAX_M0_5_P2_CLOSURE_RECHECK_PROMPT.md ]; then
  if [ ! -f audit/m0/archive/WORK_MAX_M0_5_P2_CLOSURE_RECHECK_PROMPT.md ]; then
    mv audit/m0/WORK_MAX_M0_5_P2_CLOSURE_RECHECK_PROMPT.md audit/m0/archive/
  else
    rm -f audit/m0/WORK_MAX_M0_5_P2_CLOSURE_RECHECK_PROMPT.md
  fi
fi

if [ -f audit/m0/M0_V0_5_LOCAL_VALIDATION.md ]; then
  if [ ! -f audit/m0/archive/M0_V0_5_LOCAL_VALIDATION.md ]; then
    mv audit/m0/M0_V0_5_LOCAL_VALIDATION.md audit/m0/archive/
  else
    rm -f audit/m0/M0_V0_5_LOCAL_VALIDATION.md
  fi
fi

rm -f scripts/apply_m0_v0_5_cleanup.sh

find . \
  -path './.git' -prune -o \
  -type f -name '*:Zone.Identifier' \
  -print -exec rm -f -- {} \;

find tests scripts -type d -name '__pycache__' -prune -exec rm -rf -- {} + 2>/dev/null || true
find tests scripts -type f -name '*.pyc' -delete 2>/dev/null || true

echo
echo "M0.6 cleanup complete."
echo "Tracked Zone.Identifier entries (should be empty after git add -A):"
git ls-files '*:Zone.Identifier' || true
