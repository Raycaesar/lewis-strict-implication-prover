#!/usr/bin/env python3
"""Validate M0 source/provenance and closure-readiness registers.

Normal mode checks referential integrity.
`--freeze` is a candidate-readiness gate: it rejects unresolved blocker/open/
repair-needed obligations and verifies referenced source paths exist.

It does not verify the historical truth of a citation; the closure audit does.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Mapping

import yaml

if __package__ in (None, ""):
    repo_root = Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))

from scripts.validate_spec import (
    EXPECTED_PRIMITIVE_RULES,
    EXPECTED_SCHEMA_IDS,
    EXPECTED_SYSTEMS,
    StrictLoader,
    ValidationError,
    ValidationIssue,
    load_spec_bundle,
)

DEFAULT_REGISTER = Path("audit/m0/source_register.yaml")
DEFAULT_OBLIGATIONS = Path("audit/m0/foundational_obligations.yaml")

ALLOWED_STATUSES = {
    "candidate_source_audit",
    "frozen_source_audit",
    "source_verified",
    "source_supported",
    "kernel_pending",
    "pending",
    "not_in_m0",
    "repair_implemented_reaudit_pending",
    "deferred_m2",
    "blocked",
    "open",
    "repair_needed",
    "closed",
}
UNRESOLVED_FREEZE_STATUSES = {"blocked", "open", "repair_needed"}
CLOSURE_READY_STATUSES = {
    "source_verified",
    "source_supported",
    "kernel_pending",
    "pending",
    "not_in_m0",
    "repair_implemented_reaudit_pending",
    "deferred_m2",
    "closed",
}


def _load(path: Path) -> Mapping[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise ValidationError([ValidationIssue("AUDIT_FILE_MISSING", f"missing audit file: {path}")]) from None
    try:
        data = yaml.load(text, Loader=StrictLoader)
    except yaml.YAMLError as exc:
        raise ValidationError([ValidationIssue("AUDIT_YAML_PARSE", f"{path}: {exc}")]) from None
    if not isinstance(data, Mapping):
        raise ValidationError([ValidationIssue("AUDIT_TOPLEVEL", f"{path}: top level must be a mapping")])
    return data


def _status(value: Any, path: str, issues: list[ValidationIssue]):
    if value is None:
        return
    if value not in ALLOWED_STATUSES:
        issues.append(ValidationIssue("AUDIT_STATUS", f"{path} has unrecognized status {value!r}"))


def _walk_statuses(value: Any, path: str, issues: list[ValidationIssue]):
    if isinstance(value, Mapping):
        if "status" in value:
            _status(value.get("status"), f"{path}.status", issues)
        for key, child in value.items():
            _walk_statuses(child, f"{path}.{key}", issues)
    elif isinstance(value, list):
        for i, child in enumerate(value):
            _walk_statuses(child, f"{path}[{i}]", issues)


def _check_repo_path(repo_root: Path, path_value: Any, label: str, issues):
    if not isinstance(path_value, str) or not path_value:
        issues.append(ValidationIssue("SOURCE_PATH", f"{label} has no repository_path"))
        return
    if not (repo_root / path_value).exists():
        issues.append(ValidationIssue("SOURCE_PATH_MISSING", f"{label}: {path_value} does not exist"))


def validate_source_register(
    *,
    spec_dir: Path = Path("spec"),
    register_path: Path = DEFAULT_REGISTER,
    obligations_path: Path = DEFAULT_OBLIGATIONS,
    freeze: bool = False,
    check_source_paths: bool = False,
) -> tuple[ValidationIssue, ...]:
    bundle = load_spec_bundle(spec_dir)
    register = _load(register_path)
    obligations_doc = _load(obligations_path)
    repo_root = spec_dir.resolve().parent
    issues: list[ValidationIssue] = []

    if register.get("project") != "lewis-strict-implication-prover":
        issues.append(ValidationIssue("AUDIT_PROJECT", "wrong source-register project"))
    if register.get("register_version") != "0.3":
        issues.append(ValidationIssue("AUDIT_VERSION", "M0.3 source register must have register_version 0.3"))

    top_status = register.get("status")
    _status(top_status, "source_register.status", issues)
    if freeze and top_status not in {"candidate_source_audit", "frozen_source_audit"}:
        issues.append(ValidationIssue("FREEZE_REGISTER_STATUS", "source register is not a closure candidate"))

    canonical = register.get("canonical_source")
    if not isinstance(canonical, Mapping) or canonical.get("id") != "LL1932":
        issues.append(ValidationIssue("CANONICAL_SOURCE", "canonical source must remain LL1932"))
    elif check_source_paths or freeze:
        _check_repo_path(repo_root, canonical.get("repository_path"), "canonical_source", issues)

    secondary = register.get("secondary_sources", {})
    if not isinstance(secondary, Mapping):
        issues.append(ValidationIssue("SECONDARY_SOURCES", "secondary_sources must be a mapping"))
    elif check_source_paths or freeze:
        for sid, entry in secondary.items():
            if isinstance(entry, Mapping) and entry.get("repository_path"):
                _check_repo_path(repo_root, entry.get("repository_path"), f"secondary_sources.{sid}", issues)

    schema_reg = register.get("primitive_schemas")
    if not isinstance(schema_reg, Mapping):
        issues.append(ValidationIssue("AUDIT_SCHEMA_MAP", "primitive_schemas must be a mapping"))
        schema_reg = {}
    if set(schema_reg) != set(EXPECTED_SCHEMA_IDS):
        issues.append(ValidationIssue("AUDIT_SCHEMA_IDS", "source register schema coverage mismatch"))
    if set(schema_reg) != set(bundle.schemas.get("schemas", {})):
        issues.append(ValidationIssue("AUDIT_SCHEMA_SPEC_DRIFT", "source register/spec schema ids differ"))

    operations = register.get("primitive_operations")
    if not isinstance(operations, Mapping):
        issues.append(ValidationIssue("AUDIT_RULE_MAP", "primitive_operations must be a mapping"))
        operations = {}
    if set(operations) != set(EXPECTED_PRIMITIVE_RULES):
        issues.append(ValidationIssue("AUDIT_RULE_IDS", "source register primitive operation coverage mismatch"))
    for rid, entry in operations.items():
        if not isinstance(entry, Mapping) or entry.get("project_label") != rid:
            issues.append(ValidationIssue("AUDIT_RULE_LABEL", f"{rid} project label/provenance malformed"))

    systems = register.get("normalized_systems")
    if not isinstance(systems, Mapping) or set(systems) != set(EXPECTED_SYSTEMS):
        issues.append(ValidationIssue("AUDIT_SYSTEM_IDS", "source register system coverage mismatch"))

    # Specific provenance corrections required by first audit
    parry = secondary.get("PARRY1939", {}) if isinstance(secondary, Mapping) else {}
    parry_text = " ".join(parry.get("use", [])) if isinstance(parry, Mapping) else ""
    if "11.5" not in parry_text or "McKinsey" not in parry_text:
        issues.append(ValidationIssue("PARRY_QUALIFICATION", "Parry S3 provenance must record the reduced list/11.5 qualification"))

    bridges = register.get("bridge_source_claims", {})
    for bid in ("C11_DERIVES_C10", "C11_DERIVES_C12", "C10_C12_DERIVE_C11"):
        entry = bridges.get(bid, {}) if isinstance(bridges, Mapping) else {}
        qualification = str(entry.get("source_qualification", ""))
        if "A1-A8" not in qualification or "B1-B9" not in qualification:
            issues.append(ValidationIssue("S5_P498_QUALIFICATION", f"{bid} must preserve p.498 background qualification"))
        if entry.get("canonical_s5_basis_source", {}).get("printed_page") != 501:
            issues.append(ValidationIssue("S5_P501_SOURCE", f"{bid} must cite p.501 for B1-B7 S5 presentations"))

    obligations = obligations_doc.get("obligations")
    if not isinstance(obligations, Mapping) or not obligations:
        issues.append(ValidationIssue("AUDIT_OBLIGATIONS", "obligations must be a non-empty mapping"))
        obligations = {}

    status_counts = {}
    for oid, item in obligations.items():
        if not isinstance(item, Mapping):
            issues.append(ValidationIssue("AUDIT_OBLIGATION_ENTRY", f"{oid} must be a mapping"))
            continue
        st = item.get("status")
        _status(st, f"obligations.{oid}.status", issues)
        status_counts[st] = status_counts.get(st, 0) + 1
        if freeze and st in UNRESOLVED_FREEZE_STATUSES:
            issues.append(ValidationIssue("FREEZE_UNRESOLVED", f"{oid} remains {st}"))
        severity = str(item.get("severity", ""))
        if freeze and (severity.startswith("P0") or severity.startswith("P1")) and st not in CLOSURE_READY_STATUSES:
            issues.append(ValidationIssue("FREEZE_P0_P1", f"{oid} P0/P1 status is not closure-ready: {st}"))

    if obligations_doc.get("freeze_allowed_with_open_blockers") is not False:
        issues.append(ValidationIssue("FREEZE_POLICY", "freeze_allowed_with_open_blockers must remain false"))

    if freeze:
        required_repair_ids = {"M0-D03", "M0-D04", "M0-C01", "M0-C02", "M0-C03", "M0-C04"}
        missing = required_repair_ids - set(obligations)
        if missing:
            issues.append(ValidationIssue("FREEZE_REPAIR_COVERAGE", f"missing repair obligations: {sorted(missing)}"))
        for oid in required_repair_ids & set(obligations):
            if obligations[oid].get("status") != "repair_implemented_reaudit_pending":
                issues.append(ValidationIssue("FREEZE_REPAIR_STATUS", f"{oid} is not marked repair_implemented_reaudit_pending"))

    _walk_statuses(register, "source_register", issues)

    return tuple(issues)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec-dir", type=Path, default=Path("spec"))
    parser.add_argument("--register", type=Path, default=DEFAULT_REGISTER)
    parser.add_argument("--obligations", type=Path, default=DEFAULT_OBLIGATIONS)
    parser.add_argument("--freeze", action="store_true", help="run M0.3 closure-candidate readiness checks")
    parser.add_argument("--check-source-paths", action="store_true")
    args = parser.parse_args(argv)

    try:
        issues = validate_source_register(
            spec_dir=args.spec_dir,
            register_path=args.register,
            obligations_path=args.obligations,
            freeze=args.freeze,
            check_source_paths=args.check_source_paths,
        )
    except ValidationError as exc:
        issues = exc.issues

    label = "M0 SOURCE REGISTER FREEZE READINESS" if args.freeze else "M0 SOURCE REGISTER VALIDATION"
    if issues:
        print(f"{label}: FAIL")
        for issue in issues:
            print(f"  {issue}")
        return 1

    print(f"{label}: PASS")
    print(f"  register: {args.register}")
    print(f"  obligations: {args.obligations}")
    print(f"  primitive schemas: {len(EXPECTED_SCHEMA_IDS)}")
    print(f"  primitive operations: {len(EXPECTED_PRIMITIVE_RULES)}")
    print(f"  systems: {len(EXPECTED_SYSTEMS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
