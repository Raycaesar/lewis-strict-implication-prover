#!/usr/bin/env python3
"""Validate the Lewis S1–S5 M0 executable specification.

Normal mode checks structural/policy consistency.
`--freeze` additionally checks the M0.3 closure-candidate invariants and the
independently audited AST fingerprint lock.

This is not a theorem prover and does not establish historical truth by itself.
"""

from __future__ import annotations

import argparse
import hashlib
import json
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

EXPECTED_AST_OPS = frozenset({"atom", "neg", "and", "poss", "strict_imp", "or", "equiv_s"})
EXPECTED_PRIMITIVE_RULES = ("Sa", "Sb", "Ad", "Smp")
EXPECTED_CERTIFICATE_KINDS = frozenset(
    {"postulate_instance", "Sa", "Sb", "Ad", "Smp", "definition_conversion"}
)
EXPECTED_SYSTEMS = ("S1", "S2", "S3", "S4", "S5")
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
EXPECTED_BASIS_IDS = {
    "S1": ("S1_B1_B7",),
    "S2": ("S2_B1_B8",),
    "S3": ("S3_B1_B7_A8",),
    "S4": ("S4_B1_B7_C10",),
    "S5": ("S5_PRIMARY_B1_B7_C11", "S5_ALT_B1_B7_C10_C12"),
}
ALLOWED_STATUSES = {"draft_m0", "candidate_m0", "frozen_m0"}
FORBIDDEN_CORE_AST_OPS = frozenset({"box", "material_imp", "object_equality"})


class DuplicateKeyError(ValueError):
    pass


class StrictLoader(yaml.SafeLoader):
    pass


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


StrictLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_mapping)


@dataclass(frozen=True)
class ValidationIssue:
    code: str
    message: str

    def __str__(self):
        return f"[{self.code}] {self.message}"


class ValidationError(Exception):
    def __init__(self, issues: Sequence[ValidationIssue]):
        self.issues = tuple(issues)
        super().__init__("\n".join(str(x) for x in self.issues))


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
        raise ValidationError([ValidationIssue("FILE_MISSING", f"required file is missing: {path}")]) from None
    try:
        data = yaml.load(text, Loader=StrictLoader)
    except DuplicateKeyError as exc:
        raise ValidationError([ValidationIssue("YAML_DUPLICATE_KEY", f"{path}: {exc}")]) from None
    except yaml.YAMLError as exc:
        raise ValidationError([ValidationIssue("YAML_PARSE", f"{path}: {exc}")]) from None
    if not isinstance(data, Mapping):
        raise ValidationError([ValidationIssue("YAML_TOPLEVEL", f"{path}: top level must be a mapping")])
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


def _as_mapping(value, path, issues):
    if not isinstance(value, Mapping):
        issues.append(ValidationIssue("TYPE_MAPPING", f"{path} must be a mapping"))
        return {}
    return value


def _meta_vars(node: Any) -> set[str]:
    result = set()
    if isinstance(node, Mapping):
        if set(node) == {"meta"} and isinstance(node.get("meta"), str):
            result.add(node["meta"])
        else:
            for value in node.values():
                result.update(_meta_vars(value))
    elif isinstance(node, list):
        for value in node:
            result.update(_meta_vars(value))
    return result


def _defined_op_dependencies(node: Any, defined_ops: set[str]) -> set[str]:
    result = set()
    if isinstance(node, Mapping):
        op = node.get("op")
        if op in defined_ops:
            result.add(op)
        for value in node.values():
            result.update(_defined_op_dependencies(value, defined_ops))
    return result


def _validate_ast(node, path, formula_ast, issues):
    if not isinstance(node, Mapping):
        issues.append(ValidationIssue("AST_NODE", f"{path} must be an AST/meta mapping"))
        return

    if "meta" in node:
        if set(node) != {"meta"} or not isinstance(node.get("meta"), str) or not node["meta"]:
            issues.append(ValidationIssue("META_NODE", f"{path}: malformed schema metavariable node"))
        return

    op = node.get("op")
    if not isinstance(op, str):
        issues.append(ValidationIssue("AST_OP", f"{path}: missing/non-string op"))
        return
    if op not in formula_ast:
        issues.append(ValidationIssue("UNKNOWN_AST_OP", f"{path}: unknown op {op!r}"))
        return

    decl = formula_ast[op]
    if not isinstance(decl, Mapping):
        issues.append(ValidationIssue("AST_DECL", f"formula_ast.{op} must be a mapping"))
        return

    fields = decl.get("fields")
    if not isinstance(fields, list):
        issues.append(ValidationIssue("AST_FIELDS", f"formula_ast.{op}.fields must be a list"))
        return

    actual = set(node) - {"op"}
    if actual != set(fields):
        issues.append(
            ValidationIssue("AST_FIELDS", f"{path}: fields {sorted(actual)} != declared {sorted(fields)}")
        )

    if op == "atom":
        if decl.get("arity") != 0 or fields != ["name"]:
            issues.append(ValidationIssue("ATOM_DECL", "atom must have arity 0 and fields [name]"))
        if "name" in node and (not isinstance(node["name"], str) or not node["name"]):
            issues.append(ValidationIssue("ATOM_NAME", f"{path}.name must be non-empty text"))
        return

    if decl.get("arity") != len(fields):
        issues.append(ValidationIssue("AST_ARITY", f"formula_ast.{op} arity/fields mismatch"))

    for field in fields:
        if field in node:
            _validate_ast(node[field], f"{path}.{field}", formula_ast, issues)


def _check_metadata(bundle, issues, freeze):
    versions = set()
    statuses = set()
    for component, data in bundle.components.items():
        if data.get("component") != component:
            issues.append(ValidationIssue("COMPONENT", f"{component}.yaml component mismatch"))
        if data.get("project") != PROJECT:
            issues.append(ValidationIssue("PROJECT", f"{component}.yaml project mismatch"))
        versions.add(str(data.get("spec_version")))
        status = data.get("status")
        statuses.add(status)
        if status not in ALLOWED_STATUSES:
            issues.append(ValidationIssue("STATUS", f"{component}.yaml has invalid status {status!r}"))
    if len(versions) != 1:
        issues.append(ValidationIssue("VERSION_DRIFT", f"spec versions differ: {sorted(versions)}"))
    if len(statuses) != 1:
        issues.append(ValidationIssue("STATUS_DRIFT", f"spec statuses differ: {sorted(statuses)}"))
    if freeze:
        if versions != {"0.3"}:
            issues.append(ValidationIssue("FREEZE_VERSION", "freeze candidate must be spec_version 0.3"))
        if statuses not in ({"candidate_m0"}, {"frozen_m0"}):
            issues.append(ValidationIssue("FREEZE_STATUS", "freeze candidate status must be candidate_m0 or frozen_m0"))


def _check_language(bundle, issues, freeze):
    language = bundle.language
    formula_ast = _as_mapping(language.get("formula_ast"), "language.formula_ast", issues)
    operators = _as_mapping(language.get("operators"), "language.operators", issues)

    if set(formula_ast) != set(EXPECTED_AST_OPS):
        issues.append(
            ValidationIssue(
                "AST_REGISTRY",
                f"formula_ast must be exactly {sorted(EXPECTED_AST_OPS)}; got {sorted(formula_ast)}",
            )
        )
    if FORBIDDEN_CORE_AST_OPS & set(formula_ast):
        issues.append(ValidationIssue("FORBIDDEN_AST", "forbidden core AST operator registered"))

    expected_shapes = {
        "atom": (0, ["name"]),
        "neg": (1, ["arg"]),
        "poss": (1, ["arg"]),
        "and": (2, ["left", "right"]),
        "or": (2, ["left", "right"]),
        "strict_imp": (2, ["left", "right"]),
        "equiv_s": (2, ["left", "right"]),
    }
    for op, (arity, fields) in expected_shapes.items():
        decl = formula_ast.get(op)
        if not isinstance(decl, Mapping):
            continue
        if decl.get("arity") != arity or decl.get("fields") != fields:
            issues.append(ValidationIssue("AST_SHAPE", f"{op} must have arity={arity}, fields={fields}"))

    for name, decl in operators.items():
        if not isinstance(decl, Mapping) or decl.get("ast") not in formula_ast:
            issues.append(ValidationIssue("OPERATOR_AST", f"operators.{name} refers to invalid AST"))
    if "=>" in operators.get("strict_imp", {}).get("input_aliases", []):
        issues.append(ValidationIssue("ASCII_MATERIALISH_ALIAS", "strict_imp alias '=>' is forbidden in M0.3"))

    separation = _as_mapping(language.get("meta_object_separation"), "meta_object_separation", issues)
    if separation.get("plain_equality", {}).get("allowed_in_object_formula") is not False:
        issues.append(ValidationIssue("OBJECT_EQUALITY", "plain '=' must be forbidden in object formulas"))
    deq = separation.get("definitional_equality", {})
    if deq.get("level") != "metalanguage" or deq.get("parse_as_formula") is not False:
        issues.append(ValidationIssue("DEFINITIONAL_EQUALITY", "':=' must remain metalanguage-only"))

    ep = _as_mapping(language.get("elaboration_policy"), "elaboration_policy", issues)
    if ep.get("definitions_are_inference_rules") is not False:
        issues.append(ValidationIssue("DEFINITION_RULE", "definitions cannot be Lewis inference rules"))
    if ep.get("implicit_definition_conversion_allowed") is not False:
        issues.append(ValidationIssue("IMPLICIT_DEFINITION", "implicit definition conversion must be disabled"))
    if ep.get("permit_box_sugar") is not False:
        issues.append(ValidationIssue("BOX", "Box sugar must remain disabled"))

    metadefs = _as_mapping(language.get("metadefinitions"), "metadefinitions", issues)
    expected_defs = {"DEF_OR", "DEF_STRICT_IMP", "DEF_EQUIV_S"}
    if set(metadefs) != expected_defs:
        issues.append(ValidationIssue("DEFINITION_REGISTRY", f"definition ids must be exactly {sorted(expected_defs)}"))

    defined_op_to_id = {
        op: decl.get("definition_id")
        for op, decl in formula_ast.items()
        if isinstance(decl, Mapping) and decl.get("primitive") is False
    }
    expected_map = {"or": "DEF_OR", "strict_imp": "DEF_STRICT_IMP", "equiv_s": "DEF_EQUIV_S"}
    if defined_op_to_id != expected_map:
        issues.append(ValidationIssue("DEFINED_OPERATOR_MAP", f"defined operator mapping must be {expected_map}"))

    id_to_op = {v: k for k, v in expected_map.items()}
    deps = {}
    for did, definition in metadefs.items():
        if not isinstance(definition, Mapping):
            issues.append(ValidationIssue("DEFINITION", f"{did} must be a mapping"))
            continue
        lhs, rhs = definition.get("lhs"), definition.get("rhs")
        for side_name, side in (("lhs", lhs), ("rhs", rhs)):
            _validate_ast(side, f"metadefinitions.{did}.{side_name}", formula_ast, issues)
        if isinstance(lhs, Mapping) and lhs.get("op") != id_to_op.get(did):
            issues.append(ValidationIssue("DEFINITION_LHS_ROOT", f"{did} LHS root is wrong"))
        if _meta_vars(lhs) != _meta_vars(rhs):
            issues.append(ValidationIssue("DEFINITION_METAVARS", f"{did} LHS/RHS metavariable sets differ"))
        defined_ops = set(expected_map)
        rhs_deps = _defined_op_dependencies(rhs, defined_ops)
        own = id_to_op.get(did)
        deps[own] = set(rhs_deps)

    # acyclic dependency graph over defined operators
    visiting, done = set(), set()
    def visit(op):
        if op in visiting:
            issues.append(ValidationIssue("DEFINITION_CYCLE", f"definition dependency cycle at {op}"))
            return
        if op in done:
            return
        visiting.add(op)
        for dep in deps.get(op, set()):
            visit(dep)
        visiting.remove(op)
        done.add(op)
    for op in deps:
        visit(op)

    if freeze:
        wf = _as_mapping(language.get("definition_well_formedness"), "definition_well_formedness", issues)
        if len(wf.get("requirements", [])) < 4:
            issues.append(ValidationIssue("FREEZE_DEFINITION_POLICY", "definition well-formedness requirements incomplete"))


def _check_rules(bundle, issues, freeze):
    rules = bundle.rules
    primitive = _as_mapping(rules.get("primitive_rules"), "primitive_rules", issues)
    if set(primitive) != set(EXPECTED_PRIMITIVE_RULES):
        issues.append(ValidationIssue("RULE_SET", "primitive Lewis rules must be exactly Sa,Sb,Ad,Smp"))

    expected_counts = {"Sa": 1, "Sb": 2, "Ad": 2, "Smp": 2}
    expected_required = {
        "Sa": {"kind", "parents", "atom_substitution"},
        "Sb": {"kind", "parents", "direction", "occurrence_path"},
        "Ad": {"kind", "parents"},
        "Smp": {"kind", "parents"},
    }
    for rid, count in expected_counts.items():
        rule = primitive.get(rid, {})
        if rule.get("project_label") != rid:
            issues.append(ValidationIssue("RULE_LABEL", f"{rid} project_label mismatch"))
        if rule.get("premise_count") != count:
            issues.append(ValidationIssue("RULE_PREMISES", f"{rid} premise_count must be {count}"))
        contract = rule.get("certificate_contract", {})
        if set(contract.get("required_fields", [])) != expected_required[rid]:
            issues.append(ValidationIssue("RULE_CONTRACT", f"{rid} required certificate fields are not frozen correctly"))

    path = _as_mapping(rules.get("occurrence_path_grammar"), "occurrence_path_grammar", issues)
    if path.get("root") != [] or path.get("legal_segments") != ["arg", "left", "right"]:
        issues.append(ValidationIssue("PATH_GRAMMAR", "occurrence path must use [] root and arg/left/right segments"))

    kinds = _as_mapping(rules.get("kernel_certificate_kinds"), "kernel_certificate_kinds", issues)
    if set(kinds) != set(EXPECTED_CERTIFICATE_KINDS):
        issues.append(
            ValidationIssue("CERTIFICATE_KINDS", f"trusted certificate kinds must be {sorted(EXPECTED_CERTIFICATE_KINDS)}")
        )
    dc = kinds.get("definition_conversion", {})
    if dc.get("is_lewis_inference_rule") is not False:
        issues.append(ValidationIssue("DF_RULE", "definition_conversion must not be a Lewis inference rule"))
    if dc.get("direction_values") != ["expand", "contract"]:
        issues.append(ValidationIssue("DF_DIRECTION", "definition_conversion directions must be expand/contract"))

    post = kinds.get("postulate_instance", {})
    if post.get("is_lewis_inference_rule") is not False:
        issues.append(ValidationIssue("POSTULATE_RULE", "postulate_instance is not a Lewis inference rule"))
    sub = post.get("schema_substitution", {})
    if "schema metavariables" not in str(sub.get("key_namespace", "")):
        issues.append(ValidationIssue("SCHEMA_NAMESPACE", "postulate_instance must use schema metavariable namespace"))

    sa_sub = primitive.get("Sa", {}).get("certificate_contract", {}).get("atom_substitution", {})
    if "object atom" not in str(sa_sub.get("key_namespace", "")):
        issues.append(ValidationIssue("SA_NAMESPACE", "Sa must use object atom namespace"))
    if sa_sub.get("application") != "simultaneous, one-pass, nonrecursive into replacement values":
        issues.append(ValidationIssue("SA_SEMANTICS", "Sa simultaneous one-pass nonrecursive semantics not frozen"))

    grammar = _as_mapping(rules.get("proof_node_grammar"), "proof_node_grammar", issues)
    if grammar.get("parent_reference_field") != "parents":
        issues.append(ValidationIssue("PARENT_VOCAB", "all parent references must use parents"))
    if grammar.get("no_extra_node_fields") is not True:
        issues.append(ValidationIssue("NODE_FIELDS", "proof nodes must reject extra logical fields"))

    if rules.get("explicitly_forbidden_rules", {}).get("unrestricted_necessitation", {}).get("enabled") is not False:
        issues.append(ValidationIssue("NECESSITATION", "unrestricted necessitation must be disabled"))

    if freeze and len(rules.get("dag_invariants", [])) < 6:
        issues.append(ValidationIssue("DAG_INVARIANTS", "DAG invariants are incomplete"))


def _check_schemas(bundle, issues):
    schemas = _as_mapping(bundle.schemas.get("schemas"), "schemas.schemas", issues)
    if set(schemas) != set(EXPECTED_SCHEMA_IDS):
        issues.append(ValidationIssue("SCHEMA_SET", "primitive schema registry drift"))
    if ({f"A{i}" for i in range(1, 8)} | {"B9"}) & set(schemas):
        issues.append(ValidationIssue("SCHEMA_LEAK", "A1-A7/B9 must not enter primitive registry"))
    formula_ast = bundle.language.get("formula_ast", {})
    for sid, schema in schemas.items():
        _validate_ast(schema.get("ast"), f"schemas.{sid}.ast", formula_ast, issues)
        source = schema.get("source", {})
        for field in ("work", "edition", "locus"):
            if not source.get(field):
                issues.append(ValidationIssue("SCHEMA_SOURCE", f"{sid} missing source.{field}"))


def resolve_basis(systems: Mapping[str, Any], system_id: str, *, alternative=False) -> frozenset[str]:
    visiting = []
    def resolve(current, use_alt=False):
        if current in visiting:
            raise ValueError("cyclic schema inheritance: " + " -> ".join(visiting + [current]))
        if current not in systems:
            raise ValueError(f"unknown system {current}")
        visiting.append(current)
        sys = systems[current]
        if current == "S5":
            key = "alternative_normalized_basis" if use_alt else "primary_normalized_basis"
        else:
            if use_alt:
                raise ValueError(f"{current} has no alternative basis")
            key = "normalized_basis"
        block = sys.get(key)
        if not isinstance(block, Mapping):
            raise ValueError(f"{current}.{key} missing")
        result = set()
        parent = block.get("inherit_schemas_from")
        if parent:
            result.update(resolve(parent, False))
        direct = block.get("schemas")
        additions = block.get("add_schemas")
        if direct is not None and additions is not None:
            raise ValueError(f"{current}.{key} contains schemas and add_schemas")
        chosen = direct if direct is not None else additions or []
        if not isinstance(chosen, list) or not all(isinstance(x, str) for x in chosen):
            raise ValueError(f"{current}.{key} schema list malformed")
        result.update(chosen)
        visiting.pop()
        return result
    return frozenset(resolve(system_id, alternative))


def _basis_block(systems, sid, alternative=False):
    if sid == "S5":
        key = "alternative_normalized_basis" if alternative else "primary_normalized_basis"
    else:
        key = "normalized_basis"
    return systems[sid].get(key, {})


def _check_systems(bundle, issues, freeze):
    systems_doc = bundle.systems
    systems = _as_mapping(systems_doc.get("systems"), "systems.systems", issues)
    if set(systems) != set(EXPECTED_SYSTEMS):
        issues.append(ValidationIssue("SYSTEM_SET", "system registry must be exactly S1-S5"))

    for sid in EXPECTED_SYSTEMS:
        if sid not in systems:
            continue
        try:
            resolved = resolve_basis(systems, sid)
        except ValueError as exc:
            issues.append(ValidationIssue("BASIS_RESOLUTION", f"{sid}: {exc}"))
            continue
        if resolved != EXPECTED_RESOLVED_BASES[sid]:
            issues.append(ValidationIssue("BASIS_DRIFT", f"{sid} primary/normal basis drift"))
        block = _basis_block(systems, sid)
        if set(block.get("rules", [])) != set(EXPECTED_PRIMITIVE_RULES):
            issues.append(ValidationIssue("BASIS_RULES", f"{sid} must use exactly Sa,Sb,Ad,Smp"))
        expected_bid = EXPECTED_BASIS_IDS[sid][0]
        if block.get("basis_id") != expected_bid:
            issues.append(ValidationIssue("BASIS_ID", f"{sid} basis_id must be {expected_bid}"))

    if "S5" in systems:
        if resolve_basis(systems, "S5", alternative=True) != EXPECTED_S5_ALTERNATIVE:
            issues.append(ValidationIssue("S5_ALT", "S5 alternative basis drift"))
        alt = _basis_block(systems, "S5", True)
        if alt.get("basis_id") != EXPECTED_BASIS_IDS["S5"][1]:
            issues.append(ValidationIssue("S5_ALT_ID", "S5 alternative basis_id mismatch"))
        policy = systems["S5"].get("proof_basis_policy", {})
        if policy.get("union_forbidden") is not True:
            issues.append(ValidationIssue("S5_UNION", "S5 basis union must be explicitly forbidden"))

    cp = _as_mapping(systems_doc.get("certificate_basis_policy"), "certificate_basis_policy", issues)
    if cp.get("basis_id_required_for_every_proof") is not True:
        issues.append(ValidationIssue("BASIS_REQUIRED", "every proof must require basis_id"))
    declared = cp.get("system_basis_ids")
    expected_declared = {k: list(v) for k, v in EXPECTED_BASIS_IDS.items()}
    if declared != expected_declared:
        issues.append(ValidationIssue("BASIS_REGISTRY", "certificate basis-id registry mismatch"))

    inc = systems_doc.get("theorem_inclusion", {})
    if inc.get("trusted_by_kernel_without_bridge") is not False:
        issues.append(ValidationIssue("INCLUSION_TRUST", "theorem inclusion may not bypass bridges"))

    if systems_doc.get("extensions_not_in_m0", {}).get("B9_existence", {}).get("enabled") is not False:
        issues.append(ValidationIssue("B9", "B9 must remain disabled"))


def _canonical_json(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _check_fingerprint_lock(bundle, issues):
    lock_path = bundle.spec_dir.parent / "audit/m0/certified_ast_fingerprints.yaml"
    try:
        lock = load_yaml_mapping(lock_path)
    except ValidationError as exc:
        issues.extend(exc.issues)
        return
    expected_schema = lock.get("schema_ast_sha256", {})
    expected_defs = lock.get("metadefinition_ast_sha256", {})
    if set(expected_schema) != set(EXPECTED_SCHEMA_IDS):
        issues.append(ValidationIssue("FINGERPRINT_SCHEMA_IDS", "fingerprint schema-id coverage mismatch"))
    for sid, schema in bundle.schemas.get("schemas", {}).items():
        actual = hashlib.sha256(_canonical_json(schema["ast"]).encode("utf-8")).hexdigest()
        if expected_schema.get(sid) != actual:
            issues.append(ValidationIssue("FINGERPRINT_SCHEMA", f"{sid} AST differs from audited fingerprint"))
    for did, definition in bundle.language.get("metadefinitions", {}).items():
        actual = hashlib.sha256(
            _canonical_json({"lhs": definition["lhs"], "rhs": definition["rhs"]}).encode("utf-8")
        ).hexdigest()
        if expected_defs.get(did) != actual:
            issues.append(ValidationIssue("FINGERPRINT_DEFINITION", f"{did} differs from audited fingerprint"))


def validate_bundle(bundle: SpecBundle, *, freeze=False):
    issues = []
    _check_metadata(bundle, issues, freeze)
    _check_language(bundle, issues, freeze)
    _check_rules(bundle, issues, freeze)
    _check_schemas(bundle, issues)
    _check_systems(bundle, issues, freeze)
    if freeze:
        _check_fingerprint_lock(bundle, issues)
    return tuple(issues)


def validate_spec_dir(spec_dir: Path | str = "spec", *, freeze=False) -> SpecBundle:
    bundle = load_spec_bundle(spec_dir)
    issues = validate_bundle(bundle, freeze=freeze)
    if issues:
        raise ValidationError(issues)
    return bundle


def summary_lines(bundle):
    return [
        f"spec directory: {bundle.spec_dir}",
        f"spec version: {bundle.language.get('spec_version')}",
        f"AST constructors: {len(bundle.language.get('formula_ast', {}))}",
        f"primitive schemas: {len(bundle.schemas.get('schemas', {}))}",
        f"primitive Lewis rules: {len(bundle.rules.get('primitive_rules', {}))}",
        f"trusted certificate kinds: {len(bundle.rules.get('kernel_certificate_kinds', {}))}",
        f"systems: {len(bundle.systems.get('systems', {}))}",
    ]


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec-dir", type=Path, default=Path("spec"))
    parser.add_argument("--freeze", action="store_true", help="run M0.3 closure-candidate freeze-readiness checks")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args(argv)

    try:
        bundle = validate_spec_dir(args.spec_dir, freeze=args.freeze)
    except ValidationError as exc:
        label = "M0 SPEC FREEZE READINESS" if args.freeze else "M0 SPEC VALIDATION"
        print(f"{label}: FAIL")
        for issue in exc.issues:
            print(f"  {issue}")
        return 1

    if not args.quiet:
        label = "M0 SPEC FREEZE READINESS" if args.freeze else "M0 SPEC VALIDATION"
        print(f"{label}: PASS")
        for line in summary_lines(bundle):
            print(f"  {line}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
