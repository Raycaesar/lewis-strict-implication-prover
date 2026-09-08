"""Exercise the production module CLI with positive and negative fixtures."""

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

import yaml


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests/fixtures/m1"
KINDS = ("postulate_instance", "Sa", "Sb", "Ad", "Smp", "definition_conversion")


def verify(path, expected_exit, expected_code=None, expected_detail=None, spec_root=ROOT):
    process = subprocess.run(
        [sys.executable, "-m", "lewis_prover", "verify", str(path), "--spec-root", str(spec_root)],
        cwd=ROOT, capture_output=True, text=True,
    )
    lines = process.stdout.splitlines()
    expected_status = "VALID_CERTIFICATE" if expected_exit == 0 else "INVALID_CERTIFICATE"
    if process.returncode != expected_exit or process.stderr or len(lines) != 2 or lines[0] != expected_status:
        raise SystemExit(f"CLI smoke failed for {path}: exit {process.returncode}, {process.stdout!r}, {process.stderr!r}")
    detail = json.loads(lines[1])
    if expected_code is not None and detail.get("code") != expected_code:
        raise SystemExit(f"Wrong CLI rejection for {path}: {detail}")
    if expected_detail is not None and detail.get("detail_code") != expected_detail:
        raise SystemExit(f"Wrong CLI detail for {path}: {detail}")
    print(f"PASS CLI {path.name}: {expected_status}, exit {expected_exit}" +
          (f", {detail['code']}/{detail['detail_code']}" if expected_code else ""))


def main():
    for kind in KINDS:
        verify(FIXTURES / f"{kind}.json", 0)
    invalid = FIXTURES / "invalid/definition_conversion_skipped_reverse.json"
    verify(invalid, 1, "invalid_definition_conversion", "DEFINITION_CONVERSION")
    verify(FIXTURES / "invalid/duplicate_members.json", 1, "document_decode_error", "DuplicateCertificateKeyError")

    # The exact P0 now fails during spec initialization, before any theorem check.
    with tempfile.TemporaryDirectory(prefix="lewis-m1-cli-") as temporary:
        root = Path(temporary)
        shutil.copytree(ROOT / "spec", root / "spec")
        (root / "audit/m0").mkdir(parents=True)
        for name in ("certified_ast_fingerprints.yaml", "certificate_contract_lock.yaml"):
            shutil.copy2(ROOT / "audit/m0" / name, root / "audit/m0" / name)
        language = root / "spec/language.yaml"
        document = yaml.safe_load(language.read_bytes())
        document["formula_ast"]["and"]["fields"] = ["left"]
        language.write_text(yaml.safe_dump(document, sort_keys=False, allow_unicode=True), encoding="utf-8")
        verify(invalid, 2, "frozen_spec_error", "FrozenSpecIntegrityError", root)


if __name__ == "__main__":
    main()
