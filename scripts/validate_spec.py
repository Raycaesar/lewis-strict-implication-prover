#!/usr/bin/env python3
"""Structural and M0.4 freeze-readiness validation.

This validator checks the executable specification and the closed trusted
certificate contract. It is not a theorem prover and does not replace
independent foundational audit.
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
EXPECTED_VERSION = "0.4"
EXPECTED_AST_OPS = frozenset({"atom", "neg", "and", "poss", "strict_imp", "or", "equiv_s"})
EXPECTED_PRIMITIVE_RULES = ("Sa", "Sb", "Ad", "Smp")
EXPECTED_CERTIFICATE_KINDS = frozenset(
    {"postulate_instance", "Sa", "Sb", "Ad", "Smp", "definition_conversion"}
)
EXPECTED_SCHEMA_IDS = frozenset(
    {"B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "A8", "C10", "C11", "C12"}
)
EXPECTED_SYSTEMS = ("S1", "S2", "S3", "S4", "S5")
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

EXPECTED_TOP_LEVEL_FIELDS = ["proof_id", "system", "basis_id", "goal", "root", "nodes"]
EXPECTED_JUSTIFICATION_FIELDS = {
    "postulate_instance": ["kind", "schema_id", "schema_substitution"],
    "Sa": ["kind", "parents", "atom_substitution"],
    "Sb": ["kind", "parents", "direction", "occurrence_path"],
    "Ad": ["kind", "parents"],
    "Smp": ["kind", "parents"],
    "definition_conversion": ["kind", "parents", "definition_id", "direction", "occurrence_path"],
}

FORMULA_SHAPES = {
    "atom": (0, ["name"]),
    "neg": (1, ["arg"]),
    "poss": (1, ["arg"]),
    "and": (2, ["left", "right"]),
    "or": (2, ["left", "right"]),
    "strict_imp": (2, ["left", "right"]),
    "equiv_s": (2, ["left", "right"]),
}

AUDITED_FORMULA_COMMIT = "4931e4daa124587a789ac27b841f499295facf5e"
NONREGRESSION_COMMIT = "5339a5a4f4c56a5e4feae3cc452730e488a309f1"
FINGERPRINT_LOCK_VERSION = "0.2"


class DuplicateKeyError(ValueError):
    pass


class StrictLoader(yaml.SafeLoader):
    pass


def _construct_mapping(loader, node, deep=False):
    result = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in result:
            mark = getattr(key_node, "start_mark", None)
            loc = f" line {mark.line + 1}" if mark is not None else ""
            raise DuplicateKeyError(f"duplicate YAML key {key!r}{loc}")
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


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
        raise ValidationError([ValidationIssue("FILE_MISSING", f"missing required file: {path}")]) from None
    try:
        data = yaml.load(text, Loader=StrictLoader)
    except DuplicateKeyError as exc:
        raise ValidationError([ValidationIssue("YAML_DUPLICATE_KEY", f"{path}: {exc}")]) from None
    except yaml.YAMLError as exc:
        raise ValidationError([ValidationIssue("YAML_PARSE", f"{path}: {exc}")]) from None
    if not isinstance(data, Mapping):
        raise ValidationError([ValidationIssue("YAML_TOPLEVEL", f"{path}: top level must be mapping")])
    return data


def load_spec_bundle(spec_dir: Path | str = "spec") -> SpecBundle:
    spec_dir = Path(spec_dir)
    issues = []
    loaded = {}
    for key in ("language", "rules", "schemas", "systems"):
        try:
            loaded[key] = load_yaml_mapping(spec_dir / f"{key}.yaml")
        except ValidationError as exc:
            issues.extend(exc.issues)
    if issues:
        raise ValidationError(issues)
    return SpecBundle(spec_dir, loaded["language"], loaded["rules"], loaded["schemas"], loaded["systems"])


def _m(value, path, issues):
    if not isinstance(value, Mapping):
        issues.append(ValidationIssue("TYPE_MAPPING", f"{path} must be a mapping"))
        return {}
    return value


def _validate_ast(node, path, formula_ast, issues):
    if not isinstance(node, Mapping):
        issues.append(ValidationIssue("AST_NODE", f"{path} must be mapping"))
        return
    if "meta" in node:
        if set(node) != {"meta"} or not isinstance(node.get("meta"), str) or not node["meta"]:
            issues.append(ValidationIssue("META_NODE", f"{path} malformed metavariable"))
        return
    op = node.get("op")
    if op not in formula_ast:
        issues.append(ValidationIssue("AST_OP", f"{path} unknown/missing op {op!r}"))
        return
    decl = formula_ast[op]
    fields = decl.get("fields", []) if isinstance(decl, Mapping) else []
    if set(node) - {"op"} != set(fields):
        issues.append(ValidationIssue("AST_FIELDS", f"{path} field mismatch"))
    if op == "atom":
        if decl.get("arity") != 0 or fields != ["name"]:
            issues.append(ValidationIssue("ATOM_SHAPE", "atom must be arity 0 fields [name]"))
        if not isinstance(node.get("name"), str) or not node["name"]:
            issues.append(ValidationIssue("ATOM_NAME", f"{path}.name must be nonempty string"))
        return
    if decl.get("arity") != len(fields):
        issues.append(ValidationIssue("AST_ARITY", f"{op} arity mismatch"))
    for field in fields:
        if field in node:
            _validate_ast(node[field], f"{path}.{field}", formula_ast, issues)


def _meta_vars(node):
    result = set()
    if isinstance(node, Mapping):
        if set(node) == {"meta"} and isinstance(node["meta"], str):
            result.add(node["meta"])
        else:
            for v in node.values():
                result |= _meta_vars(v)
    elif isinstance(node, list):
        for v in node:
            result |= _meta_vars(v)
    return result


def _defined_dependencies(node, defined):
    result = set()
    if isinstance(node, Mapping):
        op = node.get("op")
        if op in defined:
            result.add(op)
        for v in node.values():
            result |= _defined_dependencies(v, defined)
    return result


def _check_metadata(bundle, issues, freeze):
    versions = {str(x.get("spec_version")) for x in bundle.components.values()}
    statuses = {x.get("status") for x in bundle.components.values()}
    for name, data in bundle.components.items():
        if data.get("component") != name:
            issues.append(ValidationIssue("COMPONENT", f"{name}.yaml component mismatch"))
        if data.get("project") != PROJECT:
            issues.append(ValidationIssue("PROJECT", f"{name}.yaml project mismatch"))
    if versions != {EXPECTED_VERSION}:
        issues.append(ValidationIssue("VERSION", f"all spec versions must be {EXPECTED_VERSION}; got {sorted(versions)}"))
    if statuses != {"candidate_m0"} and statuses != {"frozen_m0"}:
        issues.append(ValidationIssue("STATUS", f"spec statuses inconsistent/not candidate: {statuses}"))
    if freeze and statuses not in ({"candidate_m0"}, {"frozen_m0"}):
        issues.append(ValidationIssue("FREEZE_STATUS", "not an M0 freeze candidate"))


def _check_language(bundle, issues):
    d = bundle.language
    ast = _m(d.get("formula_ast"), "formula_ast", issues)
    if set(ast) != set(EXPECTED_AST_OPS):
        issues.append(ValidationIssue("AST_REGISTRY", f"AST registry drift: {sorted(ast)}"))
    for op, (arity, fields) in FORMULA_SHAPES.items():
        decl = ast.get(op, {})
        if decl.get("arity") != arity or decl.get("fields") != fields:
            issues.append(ValidationIssue("AST_SHAPE", f"{op} shape drift"))
    if "=>" in d.get("operators", {}).get("strict_imp", {}).get("input_aliases", []):
        issues.append(ValidationIssue("ASCII_ALIAS", "'=>' fishhook alias forbidden"))

    ep = d.get("elaboration_policy", {})
    if ep.get("implicit_definition_conversion_allowed") is not False:
        issues.append(ValidationIssue("IMPLICIT_DEFINITION", "implicit definition conversion must be false"))
    if ep.get("definitions_are_inference_rules") is not False:
        issues.append(ValidationIssue("DEFINITION_RULE", "definitions are not Lewis rules"))
    if ep.get("permit_box_sugar") is not False:
        issues.append(ValidationIssue("BOX", "Box sugar must be false"))

    sep = d.get("meta_object_separation", {})
    if sep.get("plain_equality", {}).get("allowed_in_object_formula") is not False:
        issues.append(ValidationIssue("OBJECT_EQUALITY", "plain '=' must be forbidden"))
    if sep.get("definitional_equality", {}).get("level") != "metalanguage":
        issues.append(ValidationIssue("META_DEFINITION", "':=' must be metalanguage"))

    defs = _m(d.get("metadefinitions"), "metadefinitions", issues)
    expected = {"DEF_OR": "or", "DEF_STRICT_IMP": "strict_imp", "DEF_EQUIV_S": "equiv_s"}
    if set(defs) != set(expected):
        issues.append(ValidationIssue("DEFINITION_REGISTRY", "definition id registry drift"))
    deps = {}
    for did, op in expected.items():
        definition = defs.get(did, {})
        lhs, rhs = definition.get("lhs"), definition.get("rhs")
        _validate_ast(lhs, f"{did}.lhs", ast, issues)
        _validate_ast(rhs, f"{did}.rhs", ast, issues)
        if isinstance(lhs, Mapping) and lhs.get("op") != op:
            issues.append(ValidationIssue("DEFINITION_LHS", f"{did} LHS root must be {op}"))
        if _meta_vars(lhs) != _meta_vars(rhs):
            issues.append(ValidationIssue("DEFINITION_METAVARS", f"{did} metavariable set mismatch"))
        deps[op] = _defined_dependencies(rhs, set(expected.values()))

    visiting, done = set(), set()
    def visit(op):
        if op in visiting:
            issues.append(ValidationIssue("DEFINITION_CYCLE", f"cycle through {op}"))
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


def _check_closed_serialization(rules, issues):
    ser = _m(rules.get("certificate_serialization"), "certificate_serialization", issues)
    if ser.get("closed_world") is not True or ser.get("unknown_fields_policy") != "reject":
        issues.append(ValidationIssue("CLOSED_WORLD", "certificate serialization must be closed-world/reject unknown fields"))
    if ser.get("duplicate_mapping_keys_policy") != "reject":
        issues.append(ValidationIssue("DUPLICATE_KEYS", "duplicate mapping keys must be rejected"))
    top = ser.get("top_level", {})
    if top.get("required_fields") != EXPECTED_TOP_LEVEL_FIELDS or top.get("allowed_fields") != EXPECTED_TOP_LEVEL_FIELDS:
        issues.append(ValidationIssue("TOP_LEVEL_FIELDS", "top-level exact fields drift"))
    if top.get("unknown_fields_policy") != "reject":
        issues.append(ValidationIssue("TOP_LEVEL_UNKNOWN", "top-level unknown fields must be rejected"))

    ids = ser.get("node_id_policy", {})
    for key in ("mapping_keys_must_be", "root_must_be", "parent_references_must_be"):
        if ids.get(key) != "nonempty_string":
            issues.append(ValidationIssue("ID_TYPES", f"{key} must be nonempty_string"))
    if ids.get("reference_resolution") != "exact_string_identity_no_numeric_or_text_coercion":
        issues.append(ValidationIssue("ID_EQUALITY", "node references must use exact string identity"))

    grammar = rules.get("proof_node_grammar", {})
    if grammar.get("allowed_node_fields") != ["conclusion", "justification"]:
        issues.append(ValidationIssue("NODE_FIELDS", "node allowed fields must be conclusion/justification"))
    if grammar.get("unknown_node_fields_policy") != "reject":
        issues.append(ValidationIssue("NODE_UNKNOWN", "unknown node fields must be rejected"))
    if grammar.get("justification_unknown_fields_policy") != "reject":
        issues.append(ValidationIssue("JUSTIFICATION_UNKNOWN", "unknown justification fields must be rejected"))
    for key in ("node_id_type", "parent_reference_type", "root_reference_type"):
        if grammar.get(key) != "nonempty_string":
            issues.append(ValidationIssue("REFERENCE_TYPE", f"{key} must be nonempty_string"))


def _check_rules(bundle, issues):
    rules = bundle.rules
    primitive = _m(rules.get("primitive_rules"), "primitive_rules", issues)
    if set(primitive) != set(EXPECTED_PRIMITIVE_RULES):
        issues.append(ValidationIssue("RULE_SET", "primitive rules must be Sa/Sb/Ad/Smp"))
    kinds = _m(rules.get("kernel_certificate_kinds"), "kernel_certificate_kinds", issues)
    if set(kinds) != set(EXPECTED_CERTIFICATE_KINDS):
        issues.append(ValidationIssue("CERTIFICATE_KIND_SET", "trusted certificate kind set drift"))

    _check_closed_serialization(rules, issues)

    for rid in ("Sa", "Sb", "Ad", "Smp"):
        contract = primitive.get(rid, {}).get("certificate_contract", {})
        expected = EXPECTED_JUSTIFICATION_FIELDS[rid]
        if contract.get("required_fields") != expected or contract.get("allowed_fields") != expected:
            issues.append(ValidationIssue("RULE_ALLOWED_FIELDS", f"{rid} exact allowed fields drift"))
        if contract.get("unknown_fields_policy") != "reject":
            issues.append(ValidationIssue("RULE_UNKNOWN_FIELDS", f"{rid} unknown fields not rejected"))
        kind = kinds.get(rid, {})
        if kind.get("allowed_fields") != expected or kind.get("unknown_fields_policy") != "reject":
            issues.append(ValidationIssue("KIND_ALLOWED_FIELDS", f"{rid} kind serialization drift"))

    post = kinds.get("postulate_instance", {})
    expected = EXPECTED_JUSTIFICATION_FIELDS["postulate_instance"]
    if post.get("required_fields") != expected or post.get("allowed_fields") != expected:
        issues.append(ValidationIssue("POST_FIELDS", "postulate_instance exact fields drift"))
    if post.get("unknown_fields_policy") != "reject":
        issues.append(ValidationIssue("POST_UNKNOWN", "postulate unknown fields must be rejected"))
    sub = post.get("schema_substitution", {})
    if sub.get("domain_policy") != "exact_schema_metavariable_set":
        issues.append(ValidationIssue("POST_DOMAIN", "postulate map domain must be exact schema metavariable set"))
    if sub.get("missing_keys_policy") != "reject" or sub.get("extra_keys_policy") != "reject":
        issues.append(ValidationIssue("POST_KEYS", "missing/extra postulate keys must be rejected"))

    sa = primitive.get("Sa", {}).get("certificate_contract", {}).get("atom_substitution", {})
    if sa.get("domain_policy") != "nonempty_subset_of_parent_object_atoms":
        issues.append(ValidationIssue("SA_DOMAIN", "Sa domain policy drift"))
    if sa.get("extra_keys_policy") != "reject":
        issues.append(ValidationIssue("SA_EXTRA_KEYS", "Sa extra keys must be rejected"))
    if sa.get("application_policy") != "simultaneous_one_pass_nonrecursive":
        issues.append(ValidationIssue("SA_APPLICATION", "Sa must be simultaneous one-pass nonrecursive"))
    if sa.get("replacement_values_rewritten_by_same_substitution") is not False:
        issues.append(ValidationIssue("SA_RECURSIVE", "Sa replacement values must not be recursively rewritten"))

    sb = primitive.get("Sb", {}).get("certificate_contract", {})
    if sb.get("replacement_count") != 1:
        issues.append(ValidationIssue("SB_COUNT", "Sb must replace exactly one occurrence"))
    if sb.get("implicit_definition_conversion") != "reject":
        issues.append(ValidationIssue("SB_IMPLICIT_DF", "Sb must reject implicit definition conversion"))
    if sb.get("equivalence_root_policy") != "exact_surface_equiv_s":
        issues.append(ValidationIssue("SB_EQUIV_ROOT", "Sb equivalence root must be exact surface equiv_s"))

    dc = kinds.get("definition_conversion", {})
    expected = EXPECTED_JUSTIFICATION_FIELDS["definition_conversion"]
    if dc.get("required_fields") != expected or dc.get("allowed_fields") != expected:
        issues.append(ValidationIssue("DF_FIELDS", "definition_conversion exact fields drift"))
    if dc.get("unknown_fields_policy") != "reject":
        issues.append(ValidationIssue("DF_UNKNOWN", "definition conversion unknown fields must be rejected"))
    if dc.get("replacement_count") != 1:
        issues.append(ValidationIssue("DF_COUNT", "definition conversion must replace exactly one occurrence"))
    if dc.get("metavariable_environment_policy") != "single_shared_environment":
        issues.append(ValidationIssue("DF_ENV", "definition conversion must use one shared environment"))
    if dc.get("repeated_metavariable_policy") != "require_exact_structural_identity":
        issues.append(ValidationIssue("DF_REPEAT", "repeated definition metavariables must match exactly"))
    if dc.get("implicit_additional_conversion") != "reject":
        issues.append(ValidationIssue("DF_SECOND", "second implicit conversion must be rejected"))
    if dc.get("is_lewis_inference_rule") is not False:
        issues.append(ValidationIssue("DF_RULE", "definition_conversion is not a Lewis inference rule"))

    path = rules.get("occurrence_path_grammar", {})
    if path.get("payload_type") != "list_of_strings" or path.get("legal_segments") != ["arg", "left", "right"]:
        issues.append(ValidationIssue("PATH_GRAMMAR", "path payload/segments drift"))
    if path.get("atom_traversable_fields") != []:
        issues.append(ValidationIssue("ATOM_PATH", "atom must expose no traversable formula fields"))
    if path.get("unary_traversable_fields") != {"neg": ["arg"], "poss": ["arg"]}:
        issues.append(ValidationIssue("UNARY_PATHS", "unary traversal registry drift"))
    expected_binary = {
        "and": ["left", "right"], "or": ["left", "right"],
        "strict_imp": ["left", "right"], "equiv_s": ["left", "right"],
    }
    if path.get("binary_traversable_fields") != expected_binary:
        issues.append(ValidationIssue("BINARY_PATHS", "binary traversal registry drift"))
    if path.get("unknown_segments_policy") != "reject" or path.get("definition_expansion_during_traversal") != "forbidden":
        issues.append(ValidationIssue("PATH_POLICY", "path unknown/definition policy drift"))


def _check_schemas(bundle, issues):
    schemas = _m(bundle.schemas.get("schemas"), "schemas.schemas", issues)
    if set(schemas) != set(EXPECTED_SCHEMA_IDS):
        issues.append(ValidationIssue("SCHEMA_SET", "primitive schema registry drift"))
    ast = bundle.language.get("formula_ast", {})
    for sid, entry in schemas.items():
        _validate_ast(entry.get("ast"), f"schemas.{sid}.ast", ast, issues)


def resolve_basis(systems: Mapping[str, Any], sid: str, *, alternative=False) -> frozenset[str]:
    visiting = []
    def rec(cur, alt=False):
        if cur in visiting:
            raise ValueError("basis inheritance cycle")
        visiting.append(cur)
        if cur == "S5":
            key = "alternative_normalized_basis" if alt else "primary_normalized_basis"
        else:
            if alt:
                raise ValueError("alternative only exists for S5")
            key = "normalized_basis"
        block = systems[cur][key]
        result = set()
        parent = block.get("inherit_schemas_from")
        if parent:
            result |= rec(parent, False)
        chosen = block.get("schemas")
        if chosen is None:
            chosen = block.get("add_schemas", [])
        result |= set(chosen)
        visiting.pop()
        return result
    return frozenset(rec(sid, alternative))


def _basis_block(systems, sid, alt=False):
    if sid == "S5":
        return systems[sid]["alternative_normalized_basis" if alt else "primary_normalized_basis"]
    return systems[sid]["normalized_basis"]


def _check_systems(bundle, issues):
    doc = bundle.systems
    systems = _m(doc.get("systems"), "systems.systems", issues)
    if set(systems) != set(EXPECTED_SYSTEMS):
        issues.append(ValidationIssue("SYSTEM_SET", "system registry drift"))
        return
    for sid in EXPECTED_SYSTEMS:
        if resolve_basis(systems, sid) != EXPECTED_RESOLVED_BASES[sid]:
            issues.append(ValidationIssue("BASIS_DRIFT", f"{sid} basis drift"))
        block = _basis_block(systems, sid)
        if block.get("basis_id") != EXPECTED_BASIS_IDS[sid][0]:
            issues.append(ValidationIssue("BASIS_ID", f"{sid} basis id drift"))
        if set(block.get("rules", [])) != set(EXPECTED_PRIMITIVE_RULES):
            issues.append(ValidationIssue("BASIS_RULES", f"{sid} rule set drift"))
    if resolve_basis(systems, "S5", alternative=True) != EXPECTED_S5_ALTERNATIVE:
        issues.append(ValidationIssue("S5_ALT_BASIS", "S5 alternative basis drift"))
    if _basis_block(systems, "S5", True).get("basis_id") != EXPECTED_BASIS_IDS["S5"][1]:
        issues.append(ValidationIssue("S5_ALT_ID", "S5 alternative basis id drift"))
    if systems["S5"].get("proof_basis_policy", {}).get("union_forbidden") is not True:
        issues.append(ValidationIssue("S5_UNION", "S5 union must be forbidden"))

    policy = doc.get("certificate_basis_policy", {})
    expected_registry = {k: list(v) for k, v in EXPECTED_BASIS_IDS.items()}
    if policy.get("system_basis_ids") != expected_registry:
        issues.append(ValidationIssue("BASIS_REGISTRY", "basis registry drift"))
    if policy.get("basis_id_required_for_every_proof") is not True:
        issues.append(ValidationIssue("BASIS_REQUIRED", "basis_id required flag must be true"))
    if policy.get("bridge_metadata") != ["from_basis_id", "into_basis_id"]:
        issues.append(ValidationIssue("BRIDGE_FIELDS", "bridge metadata fields must be from/into"))
    if policy.get("bridge_expansion_rule") != "expanded_certificate.basis_id == into_basis_id":
        issues.append(ValidationIssue("BRIDGE_EXPANSION", "bridge expansion basis rule drift"))

    contract = systems["S5"].get("bridge_contract", {})
    if contract.get("expansion_requirement") != "expanded_certificate.basis_id == into_basis_id":
        issues.append(ValidationIssue("BRIDGE_CONTRACT", "S5 bridge expansion requirement drift"))
    if contract.get("field_names_are_operational") is not True:
        issues.append(ValidationIssue("BRIDGE_OPERATIONAL", "bridge field names must be operational"))

    obligations = {x["id"]: x for x in systems["S5"].get("bridge_obligations", [])}
    expected = {
        "C10_C12_DERIVE_C11": {
            "from_basis_id": EXPECTED_BASIS_IDS["S5"][0],
            "into_basis_id": EXPECTED_BASIS_IDS["S5"][1],
            "recovered_primitive_schemas": ["C11"],
            "expanded_certificate_basis_id": EXPECTED_BASIS_IDS["S5"][1],
        },
        "C11_DERIVES_C10_C12": {
            "from_basis_id": EXPECTED_BASIS_IDS["S5"][1],
            "into_basis_id": EXPECTED_BASIS_IDS["S5"][0],
            "recovered_primitive_schemas": ["C10", "C12"],
            "expanded_certificate_basis_id": EXPECTED_BASIS_IDS["S5"][0],
        },
    }
    for oid, fields in expected.items():
        ob = obligations.get(oid, {})
        for key, value in fields.items():
            if ob.get(key) != value:
                issues.append(ValidationIssue("BRIDGE_DIRECTION", f"{oid}.{key} must be {value!r}"))
        if "source_basis_id" in ob or "target_basis_id" in ob:
            issues.append(ValidationIssue("BRIDGE_LEGACY_FIELDS", f"{oid} contains legacy source/target fields"))


def _canonical_json(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _check_fingerprints(bundle, issues):
    path = bundle.spec_dir.parent / "audit/m0/certified_ast_fingerprints.yaml"
    try:
        lock = load_yaml_mapping(path)
    except ValidationError as exc:
        issues.extend(exc.issues)
        return
    if lock.get("lock_version") != FINGERPRINT_LOCK_VERSION:
        issues.append(ValidationIssue("LOCK_VERSION", "fingerprint lock_version drift"))
    if lock.get("formula_source_audit_commit") != AUDITED_FORMULA_COMMIT:
        issues.append(ValidationIssue("LOCK_SOURCE_COMMIT", "formula source-audit commit drift"))
    if lock.get("formula_nonregression_recheck_commit") != NONREGRESSION_COMMIT:
        issues.append(ValidationIssue("LOCK_RECHECK_COMMIT", "formula nonregression commit drift"))
    if "foundational change requiring explicit source re-audit" not in str(lock.get("change_policy", "")):
        issues.append(ValidationIssue("LOCK_POLICY", "fingerprint change policy missing"))

    sh = lock.get("schema_ast_sha256", {})
    dh = lock.get("metadefinition_ast_sha256", {})
    if set(sh) != set(EXPECTED_SCHEMA_IDS):
        issues.append(ValidationIssue("LOCK_SCHEMA_IDS", "schema fingerprint coverage drift"))
    for sid, entry in bundle.schemas.get("schemas", {}).items():
        actual = hashlib.sha256(_canonical_json(entry["ast"]).encode("utf-8")).hexdigest()
        if sh.get(sid) != actual:
            issues.append(ValidationIssue("FINGERPRINT_SCHEMA", f"{sid} fingerprint mismatch"))
    for did, entry in bundle.language.get("metadefinitions", {}).items():
        actual = hashlib.sha256(
            _canonical_json({"lhs": entry["lhs"], "rhs": entry["rhs"]}).encode("utf-8")
        ).hexdigest()
        if dh.get(did) != actual:
            issues.append(ValidationIssue("FINGERPRINT_DEFINITION", f"{did} fingerprint mismatch"))


def validate_bundle(bundle: SpecBundle, *, freeze=False):
    issues = []
    _check_metadata(bundle, issues, freeze)
    _check_language(bundle, issues)
    _check_rules(bundle, issues)
    _check_schemas(bundle, issues)
    _check_systems(bundle, issues)
    if freeze:
        _check_fingerprints(bundle, issues)
    return tuple(issues)


def validate_spec_dir(spec_dir: Path | str = "spec", *, freeze=False):
    bundle = load_spec_bundle(spec_dir)
    issues = validate_bundle(bundle, freeze=freeze)
    if issues:
        raise ValidationError(issues)
    return bundle


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec-dir", type=Path, default=Path("spec"))
    parser.add_argument("--freeze", action="store_true")
    args = parser.parse_args(argv)
    try:
        bundle = validate_spec_dir(args.spec_dir, freeze=args.freeze)
    except ValidationError as exc:
        label = "M0 SPEC FREEZE READINESS" if args.freeze else "M0 SPEC VALIDATION"
        print(f"{label}: FAIL")
        for issue in exc.issues:
            print(f"  {issue}")
        return 1
    label = "M0 SPEC FREEZE READINESS" if args.freeze else "M0 SPEC VALIDATION"
    print(f"{label}: PASS")
    print(f"  spec version: {bundle.language.get('spec_version')}")
    print(f"  AST constructors: {len(bundle.language.get('formula_ast', {}))}")
    print(f"  primitive schemas: {len(bundle.schemas.get('schemas', {}))}")
    print(f"  primitive Lewis rules: {len(bundle.rules.get('primitive_rules', {}))}")
    print(f"  trusted certificate kinds: {len(bundle.rules.get('kernel_certificate_kinds', {}))}")
    print(f"  systems: {len(bundle.systems.get('systems', {}))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
