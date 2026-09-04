#!/usr/bin/env bash
set -euo pipefail

if [ -x ".venv/bin/python" ]; then
  PY=".venv/bin/python"
elif command -v python3 >/dev/null 2>&1; then
  PY="$(command -v python3)"
else
  echo "No usable Python interpreter found." >&2
  exit 127
fi

echo "Using Python: $PY"
"$PY" scripts/validate_spec.py
"$PY" scripts/validate_source_register.py
"$PY" scripts/validate_spec.py --freeze
"$PY" scripts/validate_source_register.py --freeze
"$PY" -m pytest
