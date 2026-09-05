#!/usr/bin/env python3
"""Validate M0.6 source/provenance and closure-readiness registers."""

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

EXPECTED_REGISTER_VERSION = "0.6"
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
    "closed",
}
PARRY_REQUIRED_TOKENS = ("11.1-11.4", "11.6", "11.7", "30.1/A8", "11.5", "McKinsey")
PARRY_FORBIDDEN_PHRASES = (
    "11.1-11.7 together with 30.1/A8 as postulates",
    "11.1-11.7 plus 30.1/A8",
    "with 11.1-11.7",
)
CURRENT_REPAIR_PENDING = {"M0-C05", "M0-C06", "M0-V04", "M0-FP04"}


def _load(path: Path) -> Mapping[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise ValidationError([ValidationIssue("AUDIT_FILE_MISSING", f"missing: {path}")]) from None
    try:
        data = yaml.load(text, Loader=StrictLoader)
    except yaml.YAMLError as exc:
        raise ValidationError([ValidationIssue("AUDIT_YAML_PARSE", f"{path}: {exc}")]) from None
    if not isinstance(data, Mapping):
        raise ValidationError([ValidationIssue("AUDIT_TOPLEVEL", f"{path}: top level must be mapping")])
    return data


def _check_path(repo_root: Path, rel: Any, label: str, issues):
    if not isinstance(rel, str) or not rel:
        issues.append(ValidationIssue("SOURCE_PATH", f"{label} has no repository_path"))
        return
    if not (repo_root / rel).exists():
        issues.append(ValidationIssue("SOURCE_PATH_MISSING", f"{label}: {rel} missing"))


def _check_parry_text(text: Any, label: str, issues):
    s = str(text)
    for token in PARRY_REQUIRED_TOKENS:
        if token not in s:
            issues.append(ValidationIssue("PARRY_INCOMPLETE", f"{label} missing {token!r}"))
    for phrase in PARRY_FORBIDDEN_PHRASES:
        if phrase in s:
            issues.append(ValidationIssue("PARRY_INACCURATE", f"{label} retains forbidden shorthand {phrase!r}"))


def validate_source_register(
    *,
    spec_dir: Path = Path("spec"),
    register_path: Path = DEFAULT_REGISTER,
    obligations_path: Path = DEFAULT_OBLIGATIONS,
    freeze: bool = False,
) -> tuple[ValidationIssue, ...]:
    bundle = load_spec_bundle(spec_dir)
    register = _load(register_path)
    obligations_doc = _load(obligations_path)
    repo_root = spec_dir.resolve().parent
    issues = []

    if register.get("project") != "lewis-strict-implication-prover":
        issues.append(ValidationIssue("AUDIT_PROJECT", "source-register project mismatch"))
    if register.get("register_version") != EXPECTED_REGISTER_VERSION:
        issues.append(ValidationIssue("AUDIT_VERSION", f"register_version must be {EXPECTED_REGISTER_VERSION}"))
    register_status = register.get("status")
    if register_status not in {"candidate_source_audit", "frozen_source_audit"}:
        issues.append(ValidationIssue("AUDIT_STATUS", "source-register status invalid"))

    canonical = register.get("canonical_source", {})
    if canonical.get("id") != "LL1932":
        issues.append(ValidationIssue("CANONICAL_SOURCE", "canonical source must remain LL1932"))
    if freeze:
        _check_path(repo_root, canonical.get("repository_path"), "canonical_source", issues)
        for sid, entry in register.get("secondary_sources", {}).items():
            if isinstance(entry, Mapping) and entry.get("repository_path"):
                _check_path(repo_root, entry.get("repository_path"), f"secondary_sources.{sid}", issues)

    if set(register.get("primitive_schemas", {})) != set(EXPECTED_SCHEMA_IDS):
        issues.append(ValidationIssue("SCHEMA_COVERAGE", "source-register schema coverage drift"))
    if set(register.get("primitive_operations", {})) != set(EXPECTED_PRIMITIVE_RULES):
        issues.append(ValidationIssue("RULE_COVERAGE", "source-register primitive-operation coverage drift"))
    if set(register.get("normalized_systems", {})) != set(EXPECTED_SYSTEMS):
        issues.append(ValidationIssue("SYSTEM_COVERAGE", "source-register system coverage drift"))

    # Certificate-contract authority must point at exactly one machine-readable source.
    cc = register.get("certificate_contract", {})
    if cc.get("authoritative_path") != "spec/rules.yaml#canonical_certificate_contract":
        issues.append(ValidationIssue("CONTRACT_AUTHORITY_PATH", "source register contract authority path drift"))
    if cc.get("duplicate_machine_readable_semantics_allowed") is not False:
        issues.append(ValidationIssue("CONTRACT_DUPLICATION", "duplicate machine-readable certificate semantics must be forbidden"))
    if cc.get("human_documentation_status") != "nonnormative_rendering_of_canonical_contract":
        issues.append(ValidationIssue("CONTRACT_DOC_STATUS", "human certificate docs must be explicitly nonnormative renderings"))
    if cc.get("candidate_lock") != "audit/m0/certificate_contract_lock.yaml":
        issues.append(ValidationIssue("CONTRACT_LOCK_REF", "contract lock reference drift"))
    boundary = cc.get("canonical_document_boundary", {})
    if boundary.get("serialized_format") != "utf8_json_rfc8259_object":
        issues.append(ValidationIssue("CONTRACT_DOCUMENT_FORMAT", "source register canonical document format drift"))
    if boundary.get("duplicate_mapping_keys_policy") != "reject_before_mapping_construction":
        issues.append(ValidationIssue("CONTRACT_DUPLICATE_KEYS", "source register duplicate-key policy drift"))
    if boundary.get("decoder_conformance_fixture") != "scripts/certificate_document_conformance.py":
        issues.append(ValidationIssue("CONTRACT_DECODER_FIXTURE", "source register decoder fixture reference drift"))
    if cc.get("status") not in {"repair_implemented_reaudit_pending", "closed"}:
        issues.append(ValidationIssue("CONTRACT_STATUS", "certificate-contract source-register status invalid"))

    # Retain the already-closed Parry/provenance checks.
    parry_fields = {
        "source_register.secondary_sources.PARRY1939.use[0]":
            register.get("secondary_sources", {}).get("PARRY1939", {}).get("use", [""])[0],
        "source_register.primitive_schemas.A8.parry_crosscheck":
            register.get("primitive_schemas", {}).get("A8", {}).get("parry_crosscheck", ""),
        "source_register.normalized_systems.S3.normalized_basis_support.statement":
            register.get("normalized_systems", {}).get("S3", {}).get("normalized_basis_support", {}).get("statement", ""),
        "spec.schemas.schema_policy.explanation[2]":
            bundle.schemas.get("schema_policy", {}).get("explanation", ["", "", ""])[2],
        "spec.schemas.A8.normalization_note":
            bundle.schemas.get("schemas", {}).get("A8", {}).get("normalization_note", ""),
        "spec.systems.normalization_policy.key_decisions[2]":
            bundle.systems.get("normalization_policy", {}).get("key_decisions", ["", "", ""])[2],
        "spec.systems.S3.historical_basis_note":
            bundle.systems.get("systems", {}).get("S3", {}).get("historical_basis_note", ""),
    }
    for label, text in parry_fields.items():
        _check_parry_text(text, label, issues)

    bridges = register.get("bridge_source_claims", {})
    for bid in ("C11_DERIVES_C10", "C11_DERIVES_C12", "C10_C12_DERIVE_C11"):
        entry = bridges.get(bid, {})
        qual = str(entry.get("source_qualification", ""))
        if "A1-A8" not in qual or "B1-B9" not in qual or "not a native B1-B7 bridge certificate" not in qual:
            issues.append(ValidationIssue("P498_QUALIFICATION", f"{bid} p.498 qualification incomplete"))
        if entry.get("canonical_s5_basis_source", {}).get("printed_page") != 501:
            issues.append(ValidationIssue("P501_SOURCE", f"{bid} must cite p.501"))

    obligations = obligations_doc.get("obligations", {})
    if not isinstance(obligations, Mapping) or not obligations:
        issues.append(ValidationIssue("OBLIGATION_MAP", "obligations must be nonempty mapping"))
        obligations = {}

    for oid, item in obligations.items():
        if not isinstance(item, Mapping):
            issues.append(ValidationIssue("OBLIGATION_ENTRY", f"{oid} malformed"))
            continue
        st = item.get("status")
        if st not in ALLOWED_STATUSES - {"candidate_source_audit", "frozen_source_audit"}:
            issues.append(ValidationIssue("OBLIGATION_STATUS", f"{oid} has unknown/non-ready status {st!r}"))

    if obligations_doc.get("freeze_allowed_with_open_blockers") is not False:
        issues.append(ValidationIssue("FREEZE_POLICY", "freeze_allowed_with_open_blockers must remain false"))

    if freeze:
        missing = CURRENT_REPAIR_PENDING - set(obligations)
        if missing:
            issues.append(
                ValidationIssue(
                    "CURRENT_REPAIR_COVERAGE",
                    f"missing M0.6 duplicate-key repair obligations: {sorted(missing)}",
                )
            )

        for oid in CURRENT_REPAIR_PENDING & set(obligations):
            st = obligations[oid].get("status")
            if register_status == "candidate_source_audit" and st != "repair_implemented_reaudit_pending":
                issues.append(
                    ValidationIssue(
                        "CURRENT_REPAIR_STATUS",
                        f"{oid} must await re-audit in candidate mode",
                    )
                )
            if register_status == "frozen_source_audit" and st != "closed":
                issues.append(
                    ValidationIssue(
                        "FROZEN_CURRENT_REPAIR_STATUS",
                        f"{oid} must be closed in frozen mode",
                    )
                )

        if register_status == "frozen_source_audit":
            pending_ids = [
                oid for oid, item in obligations.items()
                if item.get("status") == "repair_implemented_reaudit_pending"
            ]
            if pending_ids:
                issues.append(
                    ValidationIssue(
                        "FROZEN_PENDING_REAUDIT",
                        f"frozen source register cannot retain re-audit-pending obligations: {sorted(pending_ids)}",
                    )
                )
            if cc.get("status") != "closed":
                issues.append(ValidationIssue("FROZEN_CONTRACT_STATUS", "certificate-contract register entry must be closed when frozen"))

    return tuple(issues)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec-dir", type=Path, default=Path("spec"))
    parser.add_argument("--register", type=Path, default=DEFAULT_REGISTER)
    parser.add_argument("--obligations", type=Path, default=DEFAULT_OBLIGATIONS)
    parser.add_argument("--freeze", action="store_true")
    args = parser.parse_args(argv)

    try:
        issues = validate_source_register(
            spec_dir=args.spec_dir,
            register_path=args.register,
            obligations_path=args.obligations,
            freeze=args.freeze,
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
