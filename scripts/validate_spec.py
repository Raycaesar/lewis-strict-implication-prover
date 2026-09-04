#!/usr/bin/env python3
"""Structural and policy validation for the Lewis S1–S5 M0 YAML specification.

This module deliberately does *not* implement a theorem prover and does not
duplicate the full Lewis calculus in Python. It validates the executable YAML
specification against repository-level M0 invariants: referential integrity,
AST well-formedness, normalized basis membership, and forbidden shortcuts.

Usage:
    python scripts/validate_spec.py
    python scripts/validate_spec.py --spec-dir spec
    python scripts/validate_spec.py --quiet
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence

import yaml

PROJECT = "lewis-strict-implication-prover"
SPEC_FILES = {
    "language": "language.yaml",
    "rules": "rules.yaml",
    "schemas": "schemas.yaml",
    "systems": "systems.yaml",
}

EXPECTED_PRIMITIVE_RULES = ("Sa", "Sb", "Ad", "Smp")
EXPECTED_SYSTEMS = ("S1", "S2", "S3", "S4", "S5")

# Policy-level registry checks only; formulas themselves remain solely in YAML.
EXPECTED_SCHEMA_IDS = frozenset(
    {"B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "A8", "C10", "C11", "C12"}
)

EXPECTED_RESOLVED_BASES = {
    "S1": frozenset({"B1", "B2", "B3", "B4", "B5", "B6", "B7"}),
    "S2": frozenset({"B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8"}),
    "S3": frozenset({"B1", "B2", "B3", "B4", "B5", "B6", "B7", "A8"}),
    "S4": frozenset({"B1", "B2", "B3", "B4", "B5", "B6", "B7", "C10"}),
    "S5": frozenset({"B1", "B2", "B3", "B4", "B5", "B6", "B7", "C11"}),
}
EXPECTED_S5_ALTERNATIVE = frozenset(
    {"B1", "B2", "B3", "B4", "B5", "B6", "B7", "C10", "C12"}
)

FORBIDDEN_CORE_AST_OPS = frozenset({"box", "material_imp", "object_equality"})


class DuplicateKeyError(ValueError):
    """Raised when a YAML mapping contains a duplicate key."""


class StrictLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""


def _construct_mapping(loader, node, deep=False):
    mapping = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            mark = getattr(key_node, "start_mark", None)
            where = f" at line {mark.line + 1}" if mark is not None else ""
            raise DuplicateKeyError(f"duplicate YAML key {key!r}{where}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


StrictLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping
)


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str

    def __str__(self) -> str:
        return f"[{self.code}] {self.message}"


class ValidationError(Exception):
    """Raised when one or more M0 specification checks fail."""

    def __init__(self, issues: Sequence[ValidationIssue]):
        self.issues = tuple(issues)
        super().__init__("\n".join(str(issue) for issue in self.issues))


@dataclass(frozen=True)
class SpecBundle:
    spec_dir: Path
    language: Mapping[str, Any]
    rules: Mapping[str, Any]
    schemas: Mapping[str, Any]
    systems: Mapping[str, Any]

    @property
    def components(self):
        return {
            "language": self.language,
            "rules": self.rules,
            "schemas": self.schemas,
            "systems": self.systems,
        }


def load_yaml_mapping(path: Path) -> Mapping[str, Any]:
    try:
        text = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise ValidationError(
            [ValidationIssue("FILE_MISSING", f"required file is missing: {path}")]
        ) from None

    try:
        data = yaml.load(text, Loader=StrictLoader)
    except DuplicateKeyError as exc:
        raise ValidationError(
            [ValidationIssue("YAML_DUPLICATE_KEY", f"{path}: {exc}")]
        ) from None
    except yaml.YAMLError as exc:
        raise ValidationError(
            [ValidationIssue("YAML_PARSE", f"{path}: {exc}")]
        ) from None

    if not isinstance(data, Mapping):
        raise ValidationError(
            [ValidationIssue("YAML_TOPLEVEL", f"{path}: top-level YAML must be a mapping")]
        )
    return data


def load_spec_bundle(spec_dir: Path | str = "spec") -> SpecBundle:
    spec_dir = Path(spec_dir)
    loaded = {}
    issues = []

    for component, filename in SPEC_FILES.items():
        try:
            loaded[component] = load_yaml_mapping(spec_dir / filename)
        except ValidationError as exc:
            issues.extend(exc.issues)

    if issues:
        raise ValidationError(issues)

    return SpecBundle(
        spec_dir=spec_dir,
        language=loaded["language"],
        rules=loaded["rules"],
        schemas=loaded["schemas"],
        systems=loaded["systems"],
    )


def _as_mapping(value, *, path, issues):
    if not isinstance(value, Mapping):
        issues.append(ValidationIssue("TYPE_MAPPING", f"{path} must be a YAML mapping"))
        return {}
    return value


def _validate_ast_recursively(node, *, path, formula_ast, issues):
    registered_ops = frozenset(formula_ast.keys())

    if not isinstance(node, Mapping):
        issues.append(ValidationIssue("AST_NODE", f"{path} must be an AST/meta mapping"))
        return

    if "meta" in node:
        if set(node.keys()) != {"meta"}:
            issues.append(
                ValidationIssue(
                    "META_NODE_FIELDS",
                    f"{path}: meta node must contain only the 'meta' field",
                )
            )
        value = node.get("meta")
        if not isinstance(value, str) or not value:
            issues.append(
                ValidationIssue("META_NODE_VALUE", f"{path}.meta must be non-empty text")
            )
        return

    if "op" not in node:
        issues.append(
            ValidationIssue(
                "AST_OP_MISSING",
                f"{path} is neither a meta node nor an operator node",
            )
        )
        return

    op = node.get("op")
    if not isinstance(op, str):
        issues.append(ValidationIssue("AST_OP_TYPE", f"{path}.op must be a string"))
        return

    if op in FORBIDDEN_CORE_AST_OPS:
        issues.append(
            ValidationIssue(
                "FORBIDDEN_AST_OP",
                f"{path}: forbidden M0 operator {op!r} occurs in executable AST",
            )
        )

    if op not in registered_ops:
        issues.append(
            ValidationIssue(
                "UNKNOWN_AST_OP",
                f"{path}: operator {op!r} is not registered in language.formula_ast",
            )
        )
        return

    spec = formula_ast[op]
    if not isinstance(spec, Mapping):
        issues.append(
            ValidationIssue(
                "AST_OPERATOR_SPEC",
                f"language.formula_ast.{op} must be a mapping",
            )
        )
        return

    expected_fields = spec.get("fields", [])
    if not isinstance(expected_fields, list):
        issues.append(
            ValidationIssue(
                "AST_FIELDS",
                f"language.formula_ast.{op}.fields must be a list",
            )
        )
        return

    actual_payload_fields = set(node.keys()) - {"op"}
    expected_field_set = set(expected_fields)

    if actual_payload_fields != expected_field_set:
        issues.append(
            ValidationIssue(
                "AST_ARITY_FIELDS",
                f"{path}: operator {op!r} has fields {sorted(actual_payload_fields)!r}; "
                f"expected {sorted(expected_field_set)!r}",
            )
        )

    declared_arity = spec.get("arity")

    # `atom` is terminal: its `name` field is payload, not a formula child.
    if op == "atom":
        if declared_arity != 0 or expected_fields != ["name"]:
            issues.append(
                ValidationIssue(
                    "ATOM_DECLARATION",
                    "language.formula_ast.atom must have arity: 0 and fields: [name]",
                )
            )
        if "name" in node and (
            not isinstance(node["name"], str) or not node["name"]
        ):
            issues.append(
                ValidationIssue(
                    "ATOM_NAME",
                    f"{path}.name must be a non-empty string",
                )
            )
        return

    if declared_arity != len(expected_fields):
        issues.append(
            ValidationIssue(
                "AST_DECLARED_ARITY",
                f"language.formula_ast.{op}: arity={declared_arity!r} but "
                f"fields={expected_fields!r}",
            )
        )

    for field in expected_fields:
        if field in node:
            _validate_ast_recursively(
                node[field],
                path=f"{path}.{field}",
                formula_ast=formula_ast,
                issues=issues,
            )


def _check_metadata(bundle, issues):
    versions = set()

    for expected_component, data in bundle.components.items():
        if data.get("component") != expected_component:
            issues.append(
                ValidationIssue(
                    "COMPONENT_MISMATCH",
                    f"{expected_component}.yaml declares component={data.get('component')!r}",
                )
            )
        if data.get("project") != PROJECT:
            issues.append(
                ValidationIssue(
                    "PROJECT_MISMATCH",
                    f"{expected_component}.yaml declares project={data.get('project')!r}",
                )
            )

        version = data.get("spec_version")
        if version is None:
            issues.append(
                ValidationIssue(
                    "SPEC_VERSION_MISSING",
                    f"{expected_component}.yaml has no spec_version",
                )
            )
        else:
            versions.add(str(version))

        if data.get("status") != "draft_m0":
            issues.append(
                ValidationIssue(
                    "M0_STATUS",
                    f"{expected_component}.yaml status must remain 'draft_m0' until M0 freeze",
                )
            )

    if len(versions) > 1:
        issues.append(
            ValidationIssue(
                "SPEC_VERSION_DRIFT",
                f"M0 YAML files disagree on spec_version: {sorted(versions)}",
            )
        )


def _check_language(bundle, issues):
    language = bundle.language
    formula_ast = _as_mapping(
        language.get("formula_ast"), path="language.formula_ast", issues=issues
    )
    operators = _as_mapping(
        language.get("operators"), path="language.operators", issues=issues
    )

    required_ast = {"atom", "neg", "and", "poss", "strict_imp", "or", "equiv_s"}
    missing = required_ast - set(formula_ast)
    if missing:
        issues.append(
            ValidationIssue(
                "LANGUAGE_REQUIRED_AST",
                f"language.formula_ast is missing {sorted(missing)}",
            )
        )

    leaked = FORBIDDEN_CORE_AST_OPS & set(formula_ast)
    if leaked:
        issues.append(
            ValidationIssue(
                "LANGUAGE_FORBIDDEN_AST",
                f"forbidden M0 AST constructors are registered: {sorted(leaked)}",
            )
        )

    for op, declaration in formula_ast.items():
        if not isinstance(declaration, Mapping):
            issues.append(
                ValidationIssue(
                    "AST_OPERATOR_SPEC",
                    f"language.formula_ast.{op} must be a mapping",
                )
            )
            continue
        fields = declaration.get("fields")
        arity = declaration.get("arity")
        if not isinstance(fields, list):
            issues.append(
                ValidationIssue(
                    "AST_DECLARATION",
                    f"language.formula_ast.{op}.fields must be a list",
                )
            )
        elif op == "atom":
            if arity != 0 or fields != ["name"]:
                issues.append(
                    ValidationIssue(
                        "ATOM_DECLARATION",
                        "language.formula_ast.atom must have arity: 0 and fields: [name]",
                    )
                )
        elif arity != len(fields):
            issues.append(
                ValidationIssue(
                    "AST_DECLARATION",
                    f"language.formula_ast.{op} must have arity equal to its formula-child field count",
                )
            )

    for name, declaration in operators.items():
        if not isinstance(declaration, Mapping):
            issues.append(
                ValidationIssue(
                    "OPERATOR_SPEC",
                    f"language.operators.{name} must be a mapping",
                )
            )
            continue
        ast_name = declaration.get("ast")
        if ast_name not in formula_ast:
            issues.append(
                ValidationIssue(
                    "OPERATOR_UNKNOWN_AST",
                    f"language.operators.{name}.ast={ast_name!r} is unregistered",
                )
            )

    separation = _as_mapping(
        language.get("meta_object_separation"),
        path="language.meta_object_separation",
        issues=issues,
    )
    plain_eq = _as_mapping(
        separation.get("plain_equality"),
        path="language.meta_object_separation.plain_equality",
        issues=issues,
    )
    if plain_eq.get("allowed_in_object_formula") is not False:
        issues.append(
            ValidationIssue("OBJECT_EQUALITY", "plain '=' must be forbidden in object formulas")
        )

    defeq = _as_mapping(
        separation.get("definitional_equality"),
        path="language.meta_object_separation.definitional_equality",
        issues=issues,
    )
    if defeq.get("level") != "metalanguage" or defeq.get("parse_as_formula") is not False:
        issues.append(
            ValidationIssue(
                "DEFINITIONAL_EQUALITY",
                "':=' must remain metalanguage-only",
            )
        )

    elaboration = _as_mapping(
        language.get("elaboration_policy"),
        path="language.elaboration_policy",
        issues=issues,
    )
    if elaboration.get("definitions_are_inference_rules") is not False:
        issues.append(
            ValidationIssue(
                "DEFINITIONS_AS_RULES",
                "M0 definitions must not become inference rules",
            )
        )
    if elaboration.get("permit_box_sugar") is not False:
        issues.append(
            ValidationIssue("BOX_SUGAR", "Box sugar must remain disabled in M0")
        )

    metadefs = _as_mapping(
        language.get("metadefinitions"),
        path="language.metadefinitions",
        issues=issues,
    )

    for op, declaration in formula_ast.items():
        if not isinstance(declaration, Mapping):
            continue
        definition_id = declaration.get("definition_id")
        if definition_id is not None:
            if declaration.get("primitive") is not False:
                issues.append(
                    ValidationIssue(
                        "DEFINED_PRIMITIVE_CONFLICT",
                        f"{op} has definition_id={definition_id!r} but is not primitive:false",
                    )
                )
            if definition_id not in metadefs:
                issues.append(
                    ValidationIssue(
                        "DEFINITION_MISSING",
                        f"{op} references missing metadefinition {definition_id!r}",
                    )
                )

    for definition_id, definition in metadefs.items():
        if not isinstance(definition, Mapping):
            issues.append(
                ValidationIssue(
                    "METADEFINITION_SPEC",
                    f"language.metadefinitions.{definition_id} must be a mapping",
                )
            )
            continue
        if definition.get("level") != "metalanguage":
            issues.append(
                ValidationIssue(
                    "METADEFINITION_LEVEL",
                    f"{definition_id} must be metalanguage-level",
                )
            )
        for side in ("lhs", "rhs"):
            if side not in definition:
                issues.append(
                    ValidationIssue("METADEFINITION_SIDE", f"{definition_id} is missing {side}")
                )
                continue
            _validate_ast_recursively(
                definition[side],
                path=f"language.metadefinitions.{definition_id}.{side}",
                formula_ast=formula_ast,
                issues=issues,
            )


def _check_rules(bundle, issues):
    rules = bundle.rules
    primitive_rules = _as_mapping(
        rules.get("primitive_rules"), path="rules.primitive_rules", issues=issues
    )

    actual = set(primitive_rules)
    if actual != set(EXPECTED_PRIMITIVE_RULES):
        issues.append(
            ValidationIssue(
                "PRIMITIVE_RULE_SET",
                f"primitive rules are {sorted(actual)}; expected exactly "
                f"{sorted(EXPECTED_PRIMITIVE_RULES)}",
            )
        )

    for rule_id in EXPECTED_PRIMITIVE_RULES:
        rule = primitive_rules.get(rule_id)
        if rule is None:
            continue
        if not isinstance(rule, Mapping):
            issues.append(
                ValidationIssue(
                    "RULE_SPEC",
                    f"rules.primitive_rules.{rule_id} must be a mapping",
                )
            )
            continue
        if rule.get("historical_label") != rule_id:
            issues.append(
                ValidationIssue(
                    "RULE_LABEL",
                    f"{rule_id} historical_label must remain {rule_id!r}",
                )
            )
        if not isinstance(rule.get("premise_count"), int):
            issues.append(
                ValidationIssue(
                    "RULE_PREMISE_COUNT",
                    f"{rule_id}.premise_count must be an integer",
                )
            )

    forbidden = _as_mapping(
        rules.get("explicitly_forbidden_rules"),
        path="rules.explicitly_forbidden_rules",
        issues=issues,
    )
    necessitation = _as_mapping(
        forbidden.get("unrestricted_necessitation"),
        path="rules.explicitly_forbidden_rules.unrestricted_necessitation",
        issues=issues,
    )
    if necessitation.get("enabled") is not False:
        issues.append(
            ValidationIssue(
                "NECESSITATION_ENABLED",
                "unrestricted necessitation must remain disabled",
            )
        )

    non_rules = _as_mapping(
        rules.get("non_rules"), path="rules.non_rules", issues=issues
    )
    for name in (
        "definition_expansion",
        "definition_contraction",
        "theorem_library_lookup",
        "system_inclusion",
    ):
        if name not in non_rules:
            issues.append(
                ValidationIssue(
                    "NON_RULE_MISSING",
                    f"rules.non_rules must document {name}",
                )
            )


def _check_schemas(bundle, issues):
    schemas_doc = bundle.schemas
    schemas = _as_mapping(
        schemas_doc.get("schemas"), path="schemas.schemas", issues=issues
    )

    actual_ids = frozenset(schemas)
    if actual_ids != EXPECTED_SCHEMA_IDS:
        issues.append(
            ValidationIssue(
                "SCHEMA_REGISTRY",
                f"primitive schema registry drift; "
                f"missing={sorted(EXPECTED_SCHEMA_IDS - actual_ids)}, "
                f"extra={sorted(actual_ids - EXPECTED_SCHEMA_IDS)}",
            )
        )

    forbidden_ids = {f"A{i}" for i in range(1, 8)} | {"B9"}
    leaked = forbidden_ids & actual_ids
    if leaked:
        issues.append(
            ValidationIssue(
                "OMITTED_SCHEMA_LEAK",
                f"normalized primitive registry must not contain {sorted(leaked)}",
            )
        )

    formula_ast = _as_mapping(
        bundle.language.get("formula_ast"),
        path="language.formula_ast",
        issues=issues,
    )

    for schema_id, schema in schemas.items():
        if not isinstance(schema, Mapping):
            issues.append(
                ValidationIssue(
                    "SCHEMA_SPEC",
                    f"schemas.schemas.{schema_id} must be a mapping",
                )
            )
            continue

        ast = schema.get("ast")
        if ast is None:
            issues.append(
                ValidationIssue("SCHEMA_AST_MISSING", f"{schema_id} has no ast")
            )
        else:
            _validate_ast_recursively(
                ast,
                path=f"schemas.schemas.{schema_id}.ast",
                formula_ast=formula_ast,
                issues=issues,
            )

        source = _as_mapping(
            schema.get("source"),
            path=f"schemas.schemas.{schema_id}.source",
            issues=issues,
        )
        for field in ("work", "edition", "locus"):
            if not source.get(field):
                issues.append(
                    ValidationIssue(
                        "SCHEMA_PROVENANCE",
                        f"{schema_id}.source.{field} must be present",
                    )
                )

    policy = _as_mapping(
        schemas_doc.get("schema_policy"),
        path="schemas.schema_policy",
        issues=issues,
    )
    if policy.get("no_duplicate_A1_A7") is not True:
        issues.append(
            ValidationIssue(
                "A_SERIES_POLICY",
                "schemas.schema_policy.no_duplicate_A1_A7 must remain true",
            )
        )

    omitted = _as_mapping(
        schemas_doc.get("omitted_historical_schemas"),
        path="schemas.omitted_historical_schemas",
        issues=issues,
    )
    for required in ("A1_A6", "A7", "B9"):
        if required not in omitted:
            issues.append(
                ValidationIssue(
                    "OMISSION_DOC",
                    f"omitted_historical_schemas must document {required}",
                )
            )


def resolve_basis(systems, system_id, *, alternative=False):
    """Resolve schema inheritance for one normalized system basis."""
    visiting = []

    def resolve(current, use_alternative=False):
        if current in visiting:
            cycle = " -> ".join(visiting + [current])
            raise ValueError(f"cyclic schema inheritance: {cycle}")
        if current not in systems:
            raise ValueError(f"unknown inherited system {current!r}")

        visiting.append(current)
        system = systems[current]
        if not isinstance(system, Mapping):
            raise ValueError(f"system {current!r} is not a mapping")

        if current == "S5":
            key = (
                "alternative_normalized_basis"
                if use_alternative
                else "primary_normalized_basis"
            )
        else:
            if use_alternative:
                raise ValueError(f"{current} has no alternative basis")
            key = "normalized_basis"

        block = system.get(key)
        if not isinstance(block, Mapping):
            raise ValueError(f"{current}.{key} is missing or malformed")

        result = set()
        parent = block.get("inherit_schemas_from")
        if parent is not None:
            if not isinstance(parent, str):
                raise ValueError(
                    f"{current}.{key}.inherit_schemas_from must be a string"
                )
            result.update(resolve(parent, False))

        direct = block.get("schemas")
        additions = block.get("add_schemas")
        if direct is not None and additions is not None:
            raise ValueError(
                f"{current}.{key} must not use both 'schemas' and 'add_schemas'"
            )

        chosen = direct if direct is not None else additions
        if chosen is None:
            chosen = []
        if not isinstance(chosen, list) or not all(isinstance(x, str) for x in chosen):
            raise ValueError(f"{current}.{key} schema list must contain strings")

        result.update(chosen)
        visiting.pop()
        return result

    return frozenset(resolve(system_id, alternative))


def _basis_block(systems, system_id, alternative=False):
    system = systems[system_id]
    if system_id == "S5":
        key = (
            "alternative_normalized_basis"
            if alternative
            else "primary_normalized_basis"
        )
    else:
        key = "normalized_basis"
    block = system.get(key)
    return block if isinstance(block, Mapping) else {}


def _check_systems(bundle, issues):
    systems_doc = bundle.systems
    systems = _as_mapping(
        systems_doc.get("systems"), path="systems.systems", issues=issues
    )
    schema_registry = _as_mapping(
        bundle.schemas.get("schemas"), path="schemas.schemas", issues=issues
    )
    rule_registry = _as_mapping(
        bundle.rules.get("primitive_rules"),
        path="rules.primitive_rules",
        issues=issues,
    )

    if set(systems) != set(EXPECTED_SYSTEMS):
        issues.append(
            ValidationIssue(
                "SYSTEM_REGISTRY",
                f"systems registry is {sorted(systems)}; expected {sorted(EXPECTED_SYSTEMS)}",
            )
        )

    for system_id in EXPECTED_SYSTEMS:
        if system_id not in systems:
            continue

        try:
            resolved = resolve_basis(systems, system_id)
        except ValueError as exc:
            issues.append(
                ValidationIssue("SYSTEM_BASIS_RESOLUTION", f"{system_id}: {exc}")
            )
            continue

        expected = EXPECTED_RESOLVED_BASES[system_id]
        if resolved != expected:
            issues.append(
                ValidationIssue(
                    "SYSTEM_BASIS_DRIFT",
                    f"{system_id} resolves to {sorted(resolved)}; "
                    f"expected {sorted(expected)}",
                )
            )

        unknown = resolved - set(schema_registry)
        if unknown:
            issues.append(
                ValidationIssue(
                    "SYSTEM_UNKNOWN_SCHEMA",
                    f"{system_id} references unregistered schemas {sorted(unknown)}",
                )
            )

        block = _basis_block(systems, system_id)
        basis_rules = block.get("rules")
        if not isinstance(basis_rules, list):
            issues.append(
                ValidationIssue(
                    "SYSTEM_RULES_TYPE",
                    f"{system_id} basis rules must be a list",
                )
            )
        else:
            if set(basis_rules) != set(EXPECTED_PRIMITIVE_RULES):
                issues.append(
                    ValidationIssue(
                        "SYSTEM_RULE_SET",
                        f"{system_id} basis rules are {sorted(basis_rules)}; expected "
                        f"{sorted(EXPECTED_PRIMITIVE_RULES)}",
                    )
                )
            unknown_rules = set(basis_rules) - set(rule_registry)
            if unknown_rules:
                issues.append(
                    ValidationIssue(
                        "SYSTEM_UNKNOWN_RULE",
                        f"{system_id} references unregistered rules {sorted(unknown_rules)}",
                    )
                )

    if "S5" in systems:
        try:
            alt = resolve_basis(systems, "S5", alternative=True)
        except ValueError as exc:
            issues.append(
                ValidationIssue("S5_ALT_RESOLUTION", f"S5 alternative basis: {exc}")
            )
        else:
            if alt != EXPECTED_S5_ALTERNATIVE:
                issues.append(
                    ValidationIssue(
                        "S5_ALT_BASIS_DRIFT",
                        f"S5 alternative resolves to {sorted(alt)}; expected "
                        f"{sorted(EXPECTED_S5_ALTERNATIVE)}",
                    )
                )

        alt_rules = _basis_block(systems, "S5", alternative=True).get("rules")
        if not isinstance(alt_rules, list) or set(alt_rules) != set(EXPECTED_PRIMITIVE_RULES):
            issues.append(
                ValidationIssue(
                    "S5_ALT_RULE_SET",
                    "S5 alternative basis must use exactly Sa, Sb, Ad, Smp",
                )
            )

    inclusion = _as_mapping(
        systems_doc.get("theorem_inclusion"),
        path="systems.theorem_inclusion",
        issues=issues,
    )
    if inclusion.get("trusted_by_kernel_without_bridge") is not False:
        issues.append(
            ValidationIssue(
                "THEOREM_INCLUSION_TRUST",
                "kernel must not trust theorem inclusion without bridge certificates",
            )
        )
    if inclusion.get("intended_hierarchy") != list(EXPECTED_SYSTEMS):
        issues.append(
            ValidationIssue(
                "THEOREM_HIERARCHY",
                f"intended_hierarchy must be {list(EXPECTED_SYSTEMS)!r}",
            )
        )

    extensions = _as_mapping(
        systems_doc.get("extensions_not_in_m0"),
        path="systems.extensions_not_in_m0",
        issues=issues,
    )
    b9 = _as_mapping(
        extensions.get("B9_existence"),
        path="systems.extensions_not_in_m0.B9_existence",
        issues=issues,
    )
    if b9.get("enabled") is not False:
        issues.append(
            ValidationIssue("B9_ENABLED", "B9 extension must remain disabled in M0")
        )


def validate_bundle(bundle):
    issues = []
    _check_metadata(bundle, issues)
    _check_language(bundle, issues)
    _check_rules(bundle, issues)
    _check_schemas(bundle, issues)
    _check_systems(bundle, issues)
    return tuple(issues)


def validate_spec_dir(spec_dir: Path | str = "spec") -> SpecBundle:
    bundle = load_spec_bundle(spec_dir)
    issues = validate_bundle(bundle)
    if issues:
        raise ValidationError(issues)
    return bundle


def summary_lines(bundle):
    return [
        f"spec directory: {bundle.spec_dir}",
        f"AST constructors: {len(bundle.language.get('formula_ast', {}))}",
        f"primitive schemas: {len(bundle.schemas.get('schemas', {}))}",
        f"primitive rules: {len(bundle.rules.get('primitive_rules', {}))}",
        f"systems: {len(bundle.systems.get('systems', {}))}",
    ]


def _parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--spec-dir",
        default="spec",
        type=Path,
        help="directory containing the four M0 YAML files (default: spec)",
    )
    parser.add_argument("--quiet", action="store_true", help="print only failures")
    return parser.parse_args(argv)


def main(argv=None):
    args = _parse_args(argv)
    try:
        bundle = validate_spec_dir(args.spec_dir)
    except ValidationError as exc:
        print("M0 SPEC VALIDATION: FAIL")
        for issue in exc.issues:
            print(f"  {issue}")
        return 1

    if not args.quiet:
        print("M0 SPEC VALIDATION: PASS")
        for line in summary_lines(bundle):
            print(f"  {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
