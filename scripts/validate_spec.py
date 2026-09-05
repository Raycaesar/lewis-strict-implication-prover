#!/usr/bin/env python3
"""Validate the Lewis S1–S5 M0.5 executable specification.

M0.5 has exactly one machine-readable certificate-semantics authority:
`spec/rules.yaml#canonical_certificate_contract`.

Normal mode validates structure and key invariants.
`--freeze` additionally checks the independently source-audited formula locks
and the whole canonical certificate-contract fingerprint.

This validator is not a theorem prover and cannot authenticate a deliberate
simultaneous edit of a protected object and its stored fingerprint. Such an edit
requires focused independent foundational re-audit.
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
EXPECTED_VERSION = "0.5"
EXPECTED_AST_OPS = frozenset({"atom", "neg", "and", "poss", "strict_imp", "or", "equiv_s"})
EXPECTED_PRIMITIVE_RULES = ("Sa", "Sb", "Ad", "Smp")
EXPECTED_CERTIFICATE_KINDS = (
    "postulate_instance", "Sa", "Sb", "Ad", "Smp", "definition_conversion"
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
FORMULA_SHAPES = {
    "atom": (0, ["name"]),
    "neg": (1, ["arg"]),
    "poss": (1, ["arg"]),
    "and": (2, ["left", "right"]),
    "or": (2, ["left", "right"]),
    "strict_imp": (2, ["left", "right"]),
    "equiv_s": (2, ["left", "right"]),
}

EXPECTED_RULES_TOPLEVEL_KEYS = {
    "spec_version", "component", "project", "status", "scope",
    "canonical_certificate_contract", "lewis_operations", "non_rules",
    "explicitly_forbidden_rules",
}
FORBIDDEN_LEGACY_RULES_KEYS = {
    "primitive_rules", "kernel_certificate_kinds", "occurrence_path_grammar",
    "proof_node_grammar", "dag_invariants", "certificate_serialization",
    "trusted_kernel_invariant",
}

EXPECTED_TOP_LEVEL_CERT_FIELDS = ["proof_id", "system", "basis_id", "goal", "root", "nodes"]
EXPECTED_NODE_FIELDS = ["conclusion", "justification"]
EXPECTED_KIND_FIELDS = {
    "postulate_instance": ["kind", "schema_id", "schema_substitution"],
    "Sa": ["kind", "parents", "atom_substitution"],
    "Sb": ["kind", "parents", "direction", "occurrence_path"],
    "Ad": ["kind", "parents"],
    "Smp": ["kind", "parents"],
    "definition_conversion": ["kind", "parents", "definition_id", "direction", "occurrence_path"],
}

AUDITED_FORMULA_COMMIT = "4931e4daa124587a789ac27b841f499295facf5e"
FORMULA_NONREGRESSION_COMMIT = "5339a5a4f4c56a5e4feae3cc452730e488a309f1"
AST_LOCK_VERSION = "0.2"

CONTRACT_LOCK_VERSION = "0.1"
CONTRACT_REPAIR_PARENT = "5f86547a2f16e5f1e1620823e3b68457fb8350b7"
CONTRACT_VERSION = "1.0"


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
    loaded = {}
    issues = []
    for name in ("language", "rules", "schemas", "systems"):
        try:
            loaded[name] = load_yaml_mapping(spec_dir / f"{name}.yaml")
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


def _canonical_json(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


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
    fields = decl.get("fields", [])
    if set(node) - {"op"} != set(fields):
        issues.append(ValidationIssue("AST_FIELDS", f"{path} field mismatch"))
    if op == "atom":
        if decl.get("arity") != 0 or fields != ["name"]:
            issues.append(ValidationIssue("ATOM_SHAPE", "atom must be arity 0 with fields [name]"))
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


def _check_metadata(bundle, issues):
    versions = {str(x.get("spec_version")) for x in bundle.components.values()}
    statuses = {x.get("status") for x in bundle.components.values()}
    for name, data in bundle.components.items():
        if data.get("component") != name:
            issues.append(ValidationIssue("COMPONENT", f"{name}.yaml component mismatch"))
        if data.get("project") != PROJECT:
            issues.append(ValidationIssue("PROJECT", f"{name}.yaml project mismatch"))
    if versions != {EXPECTED_VERSION}:
        issues.append(ValidationIssue("VERSION", f"all spec versions must be {EXPECTED_VERSION}; got {sorted(versions)}"))
    if statuses not in ({"candidate_m0"}, {"frozen_m0"}):
        issues.append(ValidationIssue("STATUS", f"spec statuses inconsistent/not candidate or frozen: {statuses}"))


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
        issues.append(ValidationIssue("BOX", "Box sugar must remain disabled"))

    sep = d.get("meta_object_separation", {})
    if sep.get("plain_equality", {}).get("allowed_in_object_formula") is not False:
        issues.append(ValidationIssue("OBJECT_EQUALITY", "plain '=' must be forbidden in object formulas"))
    if sep.get("definitional_equality", {}).get("level") != "metalanguage":
        issues.append(ValidationIssue("META_DEFINITION", "':=' must remain metalanguage"))

    defs = _m(d.get("metadefinitions"), "metadefinitions", issues)
    expected = {"DEF_OR": "or", "DEF_STRICT_IMP": "strict_imp", "DEF_EQUIV_S": "equiv_s"}
    if set(defs) != set(expected):
        issues.append(ValidationIssue("DEFINITION_REGISTRY", "definition registry drift"))
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


def _check_rules(bundle, issues):
    rules = bundle.rules

    # The executable rules file itself is closed under top-level keys.
    if set(rules) != EXPECTED_RULES_TOPLEVEL_KEYS:
        extra = set(rules) - EXPECTED_RULES_TOPLEVEL_KEYS
        missing = EXPECTED_RULES_TOPLEVEL_KEYS - set(rules)
        issues.append(
            ValidationIssue(
                "RULES_TOPLEVEL_KEYS",
                f"rules.yaml top-level keys drift; extra={sorted(extra)}, missing={sorted(missing)}",
            )
        )
    legacy = FORBIDDEN_LEGACY_RULES_KEYS & set(rules)
    if legacy:
        issues.append(
            ValidationIssue(
                "LEGACY_RULES_SEMANTICS",
                f"duplicate legacy certificate-semantics fields are forbidden: {sorted(legacy)}",
            )
        )

    contract = _m(rules.get("canonical_certificate_contract"), "canonical_certificate_contract", issues)
    if contract.get("contract_version") != CONTRACT_VERSION:
        issues.append(ValidationIssue("CONTRACT_VERSION", f"contract_version must be {CONTRACT_VERSION}"))
    if contract.get("authority") != "sole_machine_readable_certificate_authority":
        issues.append(ValidationIssue("CONTRACT_AUTHORITY", "canonical contract must be the sole machine-readable authority"))
    if contract.get("closed_world") is not True or contract.get("unknown_fields_policy") != "reject":
        issues.append(ValidationIssue("CONTRACT_CLOSED_WORLD", "canonical contract must be closed-world/reject unknown fields"))

    ids = contract.get("identifier_policy", {})
    expected_id_values = {
        "string_identity": "exact_unicode_codepoint_sequence_no_coercion",
        "proof_id_type": "nonempty_string",
        "node_id_type": "nonempty_string",
        "root_reference_type": "nonempty_string",
        "parent_reference_type": "nonempty_string",
        "schema_id_type": "nonempty_string",
        "definition_id_type": "nonempty_string",
        "reference_resolution": "exact_string_identity_no_numeric_or_text_coercion",
    }
    for key, value in expected_id_values.items():
        if ids.get(key) != value:
            issues.append(ValidationIssue("CONTRACT_ID_POLICY", f"identifier_policy.{key} must be {value!r}"))

    top = contract.get("top_level", {})
    if top.get("required_fields") != EXPECTED_TOP_LEVEL_CERT_FIELDS or top.get("allowed_fields") != EXPECTED_TOP_LEVEL_CERT_FIELDS:
        issues.append(ValidationIssue("CONTRACT_TOP_FIELDS", "canonical top-level certificate fields drift"))
    if top.get("unknown_fields_policy") != "reject":
        issues.append(ValidationIssue("CONTRACT_TOP_UNKNOWN", "top-level unknown fields must be rejected"))

    node = contract.get("node", {})
    if node.get("required_fields") != EXPECTED_NODE_FIELDS or node.get("allowed_fields") != EXPECTED_NODE_FIELDS:
        issues.append(ValidationIssue("CONTRACT_NODE_FIELDS", "canonical node fields drift"))
    if node.get("unknown_fields_policy") != "reject" or node.get("node_map_key_type") != "nonempty_string":
        issues.append(ValidationIssue("CONTRACT_NODE_POLICY", "canonical node closed-world/type policy drift"))

    path = contract.get("occurrence_path", {})
    expected_traversal = {
        "atom": [],
        "neg": ["arg"],
        "poss": ["arg"],
        "and": ["left", "right"],
        "or": ["left", "right"],
        "strict_imp": ["left", "right"],
        "equiv_s": ["left", "right"],
    }
    if path.get("payload_type") != "list_of_strings" or path.get("root") != []:
        issues.append(ValidationIssue("CONTRACT_PATH_TYPE", "occurrence path type/root drift"))
    if path.get("legal_segments") != ["arg", "left", "right"]:
        issues.append(ValidationIssue("CONTRACT_PATH_SEGMENTS", "occurrence path segment set drift"))
    if path.get("traversable_fields") != expected_traversal:
        issues.append(ValidationIssue("CONTRACT_PATH_TRAVERSAL", "occurrence path traversal registry drift"))
    if path.get("unknown_segments_policy") != "reject":
        issues.append(ValidationIssue("CONTRACT_PATH_UNKNOWN", "unknown path segments must be rejected"))
    if path.get("definition_expansion_during_traversal") != "forbidden":
        issues.append(ValidationIssue("CONTRACT_PATH_DF", "definition expansion during path traversal must be forbidden"))

    kinds = _m(contract.get("kinds"), "canonical_certificate_contract.kinds", issues)
    if list(kinds) != list(EXPECTED_CERTIFICATE_KINDS):
        issues.append(ValidationIssue("CONTRACT_KIND_SET", f"certificate kinds must be {list(EXPECTED_CERTIFICATE_KINDS)}"))
    for kind, expected_fields in EXPECTED_KIND_FIELDS.items():
        k = kinds.get(kind, {})
        if k.get("required_fields") != expected_fields or k.get("allowed_fields") != expected_fields:
            issues.append(ValidationIssue("CONTRACT_KIND_FIELDS", f"{kind} exact field set drift"))
        if k.get("unknown_fields_policy") != "reject":
            issues.append(ValidationIssue("CONTRACT_KIND_UNKNOWN", f"{kind} unknown fields must be rejected"))

    post = kinds.get("postulate_instance", {})
    if post.get("parent_arity") != 0 or post.get("is_lewis_inference_rule") is not False:
        issues.append(ValidationIssue("POSTULATE_ARITY", "postulate_instance must be parentless/non-rule"))
    ps = post.get("schema_substitution", {})
    expected_post = {
        "key_namespace": "schema_metavariables",
        "domain_policy": "exact_schema_metavariable_set",
        "missing_keys_policy": "reject",
        "extra_keys_policy": "reject",
        "value_type": "object_formula_without_schema_metavariables",
        "application_policy": "single_simultaneous_instantiation",
    }
    for key, value in expected_post.items():
        if ps.get(key) != value:
            issues.append(ValidationIssue("POSTULATE_SUBSTITUTION", f"postulate_instance.schema_substitution.{key} drift"))

    sa = kinds.get("Sa", {})
    if sa.get("parent_arity") != 1 or sa.get("parent_roles") != ["source_theorem"]:
        issues.append(ValidationIssue("SA_PARENTS", "Sa parent contract drift"))
    sas = sa.get("atom_substitution", {})
    expected_sa = {
        "key_namespace": "object_atom_names",
        "domain_policy": "nonempty_subset_of_parent_object_atoms",
        "extra_keys_policy": "reject",
        "unmentioned_atoms_policy": "identity",
        "value_type": "object_formula_without_schema_metavariables",
        "application_policy": "simultaneous_one_pass_nonrecursive",
        "replacement_values_rewritten_by_same_substitution": False,
    }
    for key, value in expected_sa.items():
        if sas.get(key) != value:
            issues.append(ValidationIssue("SA_SUBSTITUTION", f"Sa.atom_substitution.{key} drift"))
    if sa.get("implicit_definition_conversion") != "reject":
        issues.append(ValidationIssue("SA_IMPLICIT_DF", "Sa implicit definition conversion must be rejected"))

    sb = kinds.get("Sb", {})
    if sb.get("parent_arity") != 2 or sb.get("parent_roles") != ["equivalence_parent", "target_parent"]:
        issues.append(ValidationIssue("SB_PARENTS", "Sb parent contract drift"))
    expected_sb = {
        "direction_values": ["left_to_right", "right_to_left"],
        "equivalence_root_policy": "exact_surface_equiv_s",
        "selected_occurrence_match_policy": "exact_surface_ast_source_side",
        "replacement_count": 1,
        "root_replacement_allowed": True,
        "implicit_definition_conversion": "reject",
        "conclusion_policy": "exact_target_ast_after_one_selected_replacement",
    }
    for key, value in expected_sb.items():
        if sb.get(key) != value:
            issues.append(ValidationIssue("SB_POLICY", f"Sb.{key} drift"))

    ad = kinds.get("Ad", {})
    if ad.get("parent_arity") != 2 or ad.get("parent_roles") != ["left_parent", "right_parent"]:
        issues.append(ValidationIssue("AD_PARENTS", "Ad parent contract drift"))
    if ad.get("implicit_commutativity_or_reassociation") != "reject":
        issues.append(ValidationIssue("AD_HIDDEN_REWRITE", "Ad hidden commutativity/reassociation must be rejected"))
    if ad.get("implicit_definition_conversion") != "reject":
        issues.append(ValidationIssue("AD_IMPLICIT_DF", "Ad implicit definition conversion must be rejected"))

    smp = kinds.get("Smp", {})
    if smp.get("parent_arity") != 2 or smp.get("parent_roles") != ["antecedent_parent", "implication_parent"]:
        issues.append(ValidationIssue("SMP_PARENTS", "Smp parent contract drift"))
    if smp.get("implication_root_policy") != "exact_surface_strict_imp":
        issues.append(ValidationIssue("SMP_ROOT", "Smp implication root must be exact surface strict_imp"))
    if smp.get("antecedent_match_policy") != "exact_surface_ast":
        issues.append(ValidationIssue("SMP_ANTECEDENT", "Smp antecedent match must be exact surface AST"))
    if smp.get("implicit_definition_conversion") != "reject":
        issues.append(ValidationIssue("SMP_IMPLICIT_DF", "Smp implicit definition conversion must be rejected"))

    dc = kinds.get("definition_conversion", {})
    if dc.get("parent_arity") != 1 or dc.get("parent_roles") != ["source_parent"]:
        issues.append(ValidationIssue("DF_PARENTS", "definition_conversion parent contract drift"))
    expected_dc = {
        "direction_values": ["expand", "contract"],
        "definition_resolution_policy": "registered_metadefinition_only",
        "metavariable_environment_policy": "single_shared_environment",
        "repeated_metavariable_policy": "require_exact_structural_identity",
        "replacement_count": 1,
        "implicit_additional_conversion": "reject",
        "implicit_rule_matching_conversion": "reject",
        "conclusion_policy": "exact_surface_ast_after_one_selected_definition_replacement",
    }
    for key, value in expected_dc.items():
        if dc.get(key) != value:
            issues.append(ValidationIssue("DF_POLICY", f"definition_conversion.{key} drift"))
    if dc.get("is_lewis_inference_rule") is not False:
        issues.append(ValidationIssue("DF_RULE", "definition_conversion must not be a Lewis inference rule"))

    dag = contract.get("dag", {})
    expected_dag = {
        "node_ids_unique": True,
        "all_references_must_resolve": True,
        "acyclic": True,
        "all_nodes_reachable_from_root": True,
        "parents_accepted_before_child": True,
        "proof_formulas_forbid_schema_metavariables": True,
        "root_conclusion_exactly_equals_goal": True,
        "line_numbers_are_nonnormative_renderer_output": True,
    }
    if dag != expected_dag:
        issues.append(ValidationIssue("CONTRACT_DAG", "DAG contract drift"))
    if contract.get("metadata_policy") != "no_metadata_inside_trusted_logical_certificate":
        issues.append(ValidationIssue("CONTRACT_METADATA", "trusted logical certificate must contain no metadata field"))

    # Lewis-operation registry is provenance/label data only. It may point to
    # canonical kinds but may not duplicate executable semantics.
    ops = _m(rules.get("lewis_operations"), "lewis_operations", issues)
    if set(ops) != set(EXPECTED_PRIMITIVE_RULES):
        issues.append(ValidationIssue("LEWIS_OPERATION_SET", "Lewis operation registry drift"))
    allowed_op_keys = {"project_label", "name", "contract_kind", "source"}
    for rid in EXPECTED_PRIMITIVE_RULES:
        entry = ops.get(rid, {})
        if set(entry) != allowed_op_keys:
            issues.append(ValidationIssue("LEWIS_OPERATION_FIELDS", f"{rid} provenance entry contains semantic/extra fields"))
        if entry.get("project_label") != rid or entry.get("contract_kind") != rid:
            issues.append(ValidationIssue("LEWIS_OPERATION_LINK", f"{rid} provenance link drift"))

    if rules.get("explicitly_forbidden_rules", {}).get("unrestricted_necessitation", {}).get("enabled") is not False:
        issues.append(ValidationIssue("NECESSITATION", "unrestricted necessitation must remain disabled"))


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

    policy = doc.get("certificate_basis_policy", {})
    if policy.get("basis_id_required_for_every_proof") is not True:
        issues.append(ValidationIssue("BASIS_REQUIRED", "every proof must require basis_id"))
    if policy.get("bridge_metadata") != ["from_basis_id", "into_basis_id"]:
        issues.append(ValidationIssue("BRIDGE_FIELDS", "bridge fields must remain from_basis_id/into_basis_id"))
    if policy.get("bridge_expansion_rule") != "expanded_certificate.basis_id == into_basis_id":
        issues.append(ValidationIssue("BRIDGE_EXPANSION", "bridge expansion basis invariant drift"))

    if systems["S5"].get("proof_basis_policy", {}).get("union_forbidden") is not True:
        issues.append(ValidationIssue("S5_UNION", "S5 primary/alternative basis union must remain forbidden"))

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
            issues.append(ValidationIssue("BRIDGE_LEGACY_FIELDS", f"{oid} retains legacy source/target fields"))


def _check_ast_fingerprint_lock(bundle, issues):
    path = bundle.spec_dir.parent / "audit/m0/certified_ast_fingerprints.yaml"
    try:
        lock = load_yaml_mapping(path)
    except ValidationError as exc:
        issues.extend(exc.issues)
        return
    if lock.get("lock_version") != AST_LOCK_VERSION:
        issues.append(ValidationIssue("AST_LOCK_VERSION", "AST lock_version drift"))
    if lock.get("formula_source_audit_commit") != AUDITED_FORMULA_COMMIT:
        issues.append(ValidationIssue("AST_LOCK_SOURCE_COMMIT", "formula source-audit commit drift"))
    if lock.get("formula_nonregression_recheck_commit") != FORMULA_NONREGRESSION_COMMIT:
        issues.append(ValidationIssue("AST_LOCK_RECHECK_COMMIT", "formula nonregression commit drift"))
    sh = lock.get("schema_ast_sha256", {})
    dh = lock.get("metadefinition_ast_sha256", {})
    if set(sh) != set(EXPECTED_SCHEMA_IDS):
        issues.append(ValidationIssue("AST_LOCK_SCHEMA_IDS", "schema fingerprint coverage drift"))
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


def _check_contract_lock(bundle, issues):
    path = bundle.spec_dir.parent / "audit/m0/certificate_contract_lock.yaml"
    try:
        lock = load_yaml_mapping(path)
    except ValidationError as exc:
        issues.extend(exc.issues)
        return
    if lock.get("lock_version") != CONTRACT_LOCK_VERSION:
        issues.append(ValidationIssue("CONTRACT_LOCK_VERSION", "certificate contract lock_version drift"))
    if lock.get("repair_parent_commit") != CONTRACT_REPAIR_PARENT:
        issues.append(ValidationIssue("CONTRACT_LOCK_PARENT", "certificate contract repair-parent commit drift"))
    if lock.get("contract_path") != "spec/rules.yaml#canonical_certificate_contract":
        issues.append(ValidationIssue("CONTRACT_LOCK_PATH", "certificate contract lock path drift"))
    if lock.get("contract_version") != CONTRACT_VERSION:
        issues.append(ValidationIssue("CONTRACT_LOCK_CONTRACT_VERSION", "certificate contract lock version mismatch"))
    policy = str(lock.get("change_policy", ""))
    if "focused independent re-audit" not in policy or "simultaneous" not in policy:
        issues.append(ValidationIssue("CONTRACT_LOCK_POLICY", "certificate contract change/re-audit policy incomplete"))

    contract = bundle.rules.get("canonical_certificate_contract")
    actual = hashlib.sha256(_canonical_json(contract).encode("utf-8")).hexdigest()
    if lock.get("canonical_contract_sha256") != actual:
        issues.append(ValidationIssue("FINGERPRINT_CONTRACT", "canonical certificate contract fingerprint mismatch"))


def validate_bundle(bundle: SpecBundle, *, freeze=False):
    issues = []
    _check_metadata(bundle, issues)
    _check_language(bundle, issues)
    _check_rules(bundle, issues)
    _check_schemas(bundle, issues)
    _check_systems(bundle, issues)
    if freeze:
        _check_ast_fingerprint_lock(bundle, issues)
        _check_contract_lock(bundle, issues)
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
    print(f"  Lewis operations: {len(bundle.rules.get('lewis_operations', {}))}")
    print(f"  trusted certificate kinds: {len(bundle.rules.get('canonical_certificate_contract', {}).get('kinds', {}))}")
    print(f"  systems: {len(bundle.systems.get('systems', {}))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
