#!/usr/bin/env bash
set -euo pipefail

echo "Applying M0.4.1 integration cleanup..."

# Archive/remove superseded active foundational spec.
mkdir -p docs/archive
if [ -f docs/FOUNDATIONAL_SPEC_v0.3.md ]; then
  if [ ! -f docs/archive/FOUNDATIONAL_SPEC_v0.3.md ]; then
    mv docs/FOUNDATIONAL_SPEC_v0.3.md docs/archive/FOUNDATIONAL_SPEC_v0.3.md
  else
    rm -f docs/FOUNDATIONAL_SPEC_v0.3.md
  fi
fi

# Remove stale v0.3 test modules. These were replaced by the M0.4 suite, but
# ZIP overlay extraction does not delete files that disappeared from a package.
stale_tests=(
  tests/spec/test_language_spec.py
  tests/spec/test_rule_spec.py
  tests/spec/test_schema_spec.py
  tests/spec/test_source_register.py
  tests/spec/test_system_spec.py
  tests/spec/test_validator.py
)

echo "Removing superseded v0.3 tests if present..."
for f in "${stale_tests[@]}"; do
  if [ -f "$f" ]; then
    echo "  remove $f"
    rm -f -- "$f"
  fi
done

# Remove materialized Windows Mark-of-the-Web metadata without find -delete.
echo "Removing Zone.Identifier files..."
find . \
  -path './.git' -prune -o \
  -type f -name '*:Zone.Identifier' \
  -print -exec rm -f -- {} \;

# Clear Python bytecode caches so deleted test modules cannot be rediscovered
# from stale cache artifacts by unusual tooling.
find tests scripts -type d -name '__pycache__' -prune -exec rm -rf -- {} + 2>/dev/null || true
find tests scripts -type f -name '*.pyc' -delete 2>/dev/null || true

echo
echo "Cleanup complete."
echo "Expected active M0.4 test files:"
find tests/spec -maxdepth 1 -type f -name 'test_*.py' -printf '  %f\n' | sort
echo
echo "Tracked Zone.Identifier entries (should be empty after git add -A):"
git ls-files '*:Zone.Identifier' || true
