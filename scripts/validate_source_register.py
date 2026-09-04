#!/usr/bin/env python3
"""Validate M0 source/provenance registers against the executable spec.

This is a referential-integrity validator. It does NOT decide whether the
historical claims in the register are true; that remains a human/Work Max
source-audit task.
"""

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any, Mapping
import sys

import yaml

# When executed as `python scripts/validate_source_register.py`, Python places
# `scripts/` rather than the repository root on sys.path. Add the root so the
# package import below behaves the same locally, in pytest, and in CI.
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
    "draft_source_audit",
    "source_verified",
    "source_supported",
    "open",
    "repair_needed",
    "kernel_pending",
    "blocked",
    "not_in_m0",
    "pending",
}


def _load_mapping(path: Path) -> Mapping[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise ValidationError(
            [ValidationIssue("AUDIT_FILE_MISSING", f"missing audit file: {path}")]
        ) from None

    try:
        data = yaml.load(text, Loader=StrictLoader)
    except yaml.YAMLError as exc:
        raise ValidationError(
            [ValidationIssue("AUDIT_YAML_PARSE", f"{path}: {exc}")]
        ) from None

    if not isinstance(data, Mapping):
        raise ValidationError(
            [ValidationIssue("AUDIT_TOPLEVEL", f"{path}: top level must be a mapping")]
        )
    return data


def _check_status(value: Any, path: str, issues: list[ValidationIssue]) -> None:
    if value is None:
        return
    if value not in ALLOWED_STATUSES:
        issues.append(
            ValidationIssue(
                "AUDIT_STATUS",
                f"{path} has unrecognized status {value!r}",
            )
        )


def _walk_statuses(value: Any, path: str, issues: list[ValidationIssue]) -> None:
    if isinstance(value, Mapping):
        if "status" in value:
            _check_status(value.get("status"), f"{path}.status", issues)
        for key, child in value.items():
            _walk_statuses(child, f"{path}.{key}", issues)
    elif isinstance(value, list):
        for i, child in enumerate(value):
            _walk_statuses(child, f"{path}[{i}]", issues)


def validate_source_register(
    *,
    spec_dir: Path = Path("spec"),
    register_path: Path = DEFAULT_REGISTER,
    obligations_path: Path = DEFAULT_OBLIGATIONS,
) -> tuple[ValidationIssue, ...]:
    bundle = load_spec_bundle(spec_dir)
    register = _load_mapping(register_path)
    obligations_doc = _load_mapping(obligations_path)
    issues: list[ValidationIssue] = []

    if register.get("project") != "lewis-strict-implication-prover":
        issues.append(
            ValidationIssue("AUDIT_PROJECT", "source register project identifier is wrong")
        )

    canonical = register.get("canonical_source")
    if not isinstance(canonical, Mapping):
        issues.append(
            ValidationIssue("AUDIT_CANONICAL_SOURCE", "canonical_source must be a mapping")
        )
    else:
        if canonical.get("id") != "LL1932":
            issues.append(
                ValidationIssue(
                    "AUDIT_CANONICAL_SOURCE",
                    "canonical source id must remain LL1932 during M0",
                )
            )
        repo_path = canonical.get("repository_path")
        if not isinstance(repo_path, str) or not repo_path:
            issues.append(
                ValidationIssue(
                    "AUDIT_CANONICAL_PATH",
                    "canonical source must record repository_path",
                )
            )

    # Every executable primitive schema must have a source-register entry,
    # and no unknown executable schema may appear there.
    schema_register = register.get("primitive_schemas")
    if not isinstance(schema_register, Mapping):
        issues.append(
            ValidationIssue("AUDIT_SCHEMA_MAP", "primitive_schemas must be a mapping")
        )
        schema_register = {}

    registered_schema_ids = set(schema_register)
    if registered_schema_ids != set(EXPECTED_SCHEMA_IDS):
        issues.append(
            ValidationIssue(
                "AUDIT_SCHEMA_IDS",
                f"source-register primitive schema ids are {sorted(registered_schema_ids)}; "
                f"expected {sorted(EXPECTED_SCHEMA_IDS)}",
            )
        )

    executable_schema_ids = set(bundle.schemas.get("schemas", {}))
    if registered_schema_ids != executable_schema_ids:
        issues.append(
            ValidationIssue(
                "AUDIT_SCHEMA_SPEC_DRIFT",
                "source-register schema ids and spec/schemas.yaml have drifted",
            )
        )

    # Every primitive operation must be registered by its project label.
    operations = register.get("primitive_operations")
    if not isinstance(operations, Mapping):
        issues.append(
            ValidationIssue("AUDIT_RULE_MAP", "primitive_operations must be a mapping")
        )
        operations = {}

    if set(operations) != set(EXPECTED_PRIMITIVE_RULES):
        issues.append(
            ValidationIssue(
                "AUDIT_RULE_IDS",
                f"source-register primitive operations are {sorted(operations)}; "
                f"expected {sorted(EXPECTED_PRIMITIVE_RULES)}",
            )
        )

    for rule_id, entry in operations.items():
        if not isinstance(entry, Mapping):
            issues.append(
                ValidationIssue(
                    "AUDIT_RULE_ENTRY",
                    f"primitive_operations.{rule_id} must be a mapping",
                )
            )
            continue
        if entry.get("project_label") != rule_id:
            issues.append(
                ValidationIssue(
                    "AUDIT_RULE_LABEL",
                    f"primitive_operations.{rule_id}.project_label must equal {rule_id}",
                )
            )
        source = entry.get("source")
        if not isinstance(source, Mapping) or source.get("source_id") != "LL1932":
            issues.append(
                ValidationIssue(
                    "AUDIT_RULE_SOURCE",
                    f"{rule_id} must carry canonical LL1932 provenance",
                )
            )

    systems = register.get("normalized_systems")
    if not isinstance(systems, Mapping):
        issues.append(
            ValidationIssue("AUDIT_SYSTEM_MAP", "normalized_systems must be a mapping")
        )
        systems = {}

    if set(systems) != set(EXPECTED_SYSTEMS):
        issues.append(
            ValidationIssue(
                "AUDIT_SYSTEM_IDS",
                f"source-register systems are {sorted(systems)}; "
                f"expected {sorted(EXPECTED_SYSTEMS)}",
            )
        )

    # Obligations must have stable unique ids by mapping construction and
    # freeze blockers must be explicit.
    obligations = obligations_doc.get("obligations")
    if not isinstance(obligations, Mapping) or not obligations:
        issues.append(
            ValidationIssue("AUDIT_OBLIGATIONS", "obligations must be a non-empty mapping")
        )
        obligations = {}

    blockers = []
    for obligation_id, obligation in obligations.items():
        if not isinstance(obligation, Mapping):
            issues.append(
                ValidationIssue(
                    "AUDIT_OBLIGATION_ENTRY",
                    f"obligations.{obligation_id} must be a mapping",
                )
            )
            continue
        status = obligation.get("status")
        _check_status(status, f"obligations.{obligation_id}.status", issues)
        if status == "blocked":
            blockers.append(obligation_id)

    if obligations_doc.get("freeze_allowed_with_open_blockers") is not False:
        issues.append(
            ValidationIssue(
                "AUDIT_FREEZE_POLICY",
                "freeze_allowed_with_open_blockers must remain false",
            )
        )

    if not blockers:
        issues.append(
            ValidationIssue(
                "AUDIT_BLOCKER_VISIBILITY",
                "M0 audit register currently expects explicit blockers before final audit; "
                "if all blockers are closed, update this validator together with the freeze state",
            )
        )

    _walk_statuses(register, "source_register", issues)

    return tuple(issues)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec-dir", type=Path, default=Path("spec"))
    parser.add_argument("--register", type=Path, default=DEFAULT_REGISTER)
    parser.add_argument("--obligations", type=Path, default=DEFAULT_OBLIGATIONS)
    args = parser.parse_args(argv)

    try:
        issues = validate_source_register(
            spec_dir=args.spec_dir,
            register_path=args.register,
            obligations_path=args.obligations,
        )
    except ValidationError as exc:
        issues = exc.issues

    if issues:
        print("M0 SOURCE REGISTER VALIDATION: FAIL")
        for issue in issues:
            print(f"  {issue}")
        return 1

    print("M0 SOURCE REGISTER VALIDATION: PASS")
    print(f"  register: {args.register}")
    print(f"  obligations: {args.obligations}")
    print(f"  expected primitive schemas: {len(EXPECTED_SCHEMA_IDS)}")
    print(f"  expected primitive operations: {len(EXPECTED_PRIMITIVE_RULES)}")
    print(f"  expected systems: {len(EXPECTED_SYSTEMS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
