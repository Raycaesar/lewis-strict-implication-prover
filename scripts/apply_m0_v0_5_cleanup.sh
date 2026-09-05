#!/usr/bin/env bash
set -euo pipefail

echo "Applying M0.5 repository cleanup..."

mkdir -p docs/archive audit/m0/archive

if [ -f docs/FOUNDATIONAL_SPEC_v0.4.md ]; then
  if [ ! -f docs/archive/FOUNDATIONAL_SPEC_v0.4.md ]; then
    mv docs/FOUNDATIONAL_SPEC_v0.4.md docs/archive/FOUNDATIONAL_SPEC_v0.4.md
  else
    rm -f docs/FOUNDATIONAL_SPEC_v0.4.md
  fi
fi

if [ -f audit/m0/WORK_MAX_M0_4_CLOSURE_RECHECK_PROMPT.md ]; then
  if [ ! -f audit/m0/archive/WORK_MAX_M0_4_CLOSURE_RECHECK_PROMPT.md ]; then
    mv audit/m0/WORK_MAX_M0_4_CLOSURE_RECHECK_PROMPT.md \
       audit/m0/archive/WORK_MAX_M0_4_CLOSURE_RECHECK_PROMPT.md
  else
    rm -f audit/m0/WORK_MAX_M0_4_CLOSURE_RECHECK_PROMPT.md
  fi
fi



rm -f scripts/apply_m0_v0_4_cleanup.sh
rm -f M0_V0_4_1_HOTFIX_README.md

find . \
  -path './.git' -prune -o \
  -type f -name '*:Zone.Identifier' \
  -print -exec rm -f -- {} \;

find tests scripts -type d -name '__pycache__' -prune -exec rm -rf -- {} + 2>/dev/null || true
find tests scripts -type f -name '*.pyc' -delete 2>/dev/null || true

echo "M0.5 cleanup complete."
