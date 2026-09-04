import copy
import yaml

from scripts.validate_spec import StrictLoader, load_spec_bundle, validate_bundle


EXPECTED_AST = {"atom", "neg", "and", "poss", "strict_imp", "or", "equiv_s"}


def test_formula_ast_registry_is_exact(spec_bundle):
    assert set(spec_bundle.language["formula_ast"]) == EXPECTED_AST


def test_core_meta_object_separation(spec_bundle):
    sep = spec_bundle.language["meta_object_separation"]
    assert sep["plain_equality"]["allowed_in_object_formula"] is False
    assert sep["definitional_equality"]["level"] == "metalanguage"
    assert sep["definitional_equality"]["parse_as_formula"] is False


def test_no_box_or_materialish_arrow_alias(spec_bundle):
    assert "box" not in spec_bundle.language["formula_ast"]
    assert "=>" not in spec_bundle.language["operators"]["strict_imp"]["input_aliases"]
    assert spec_bundle.language["elaboration_policy"]["permit_box_sugar"] is False


def test_definition_policy_is_explicit_and_nonimplicit(spec_bundle):
    policy = spec_bundle.language["elaboration_policy"]
    assert policy["definitions_are_inference_rules"] is False
    assert policy["implicit_definition_conversion_allowed"] is False
    assert "exact structural identity" in policy["surface_formula_identity"]


def test_definition_metavariable_sets_match(spec_bundle):
    from scripts.validate_spec import _meta_vars
    for did, definition in spec_bundle.language["metadefinitions"].items():
        assert _meta_vars(definition["lhs"]) == _meta_vars(definition["rhs"]), did


def test_validator_rejects_extra_ast_constructor(spec_bundle):
    language = copy.deepcopy(spec_bundle.language)
    language["formula_ast"]["box"] = {"arity": 1, "fields": ["arg"], "primitive": True}
    mutated = type(spec_bundle)(
        spec_bundle.spec_dir, language, spec_bundle.rules, spec_bundle.schemas, spec_bundle.systems
    )
    issues = validate_bundle(mutated)
    assert any(i.code in {"AST_REGISTRY", "FORBIDDEN_AST"} for i in issues)


def test_validator_rejects_recursive_definition(spec_bundle):
    language = copy.deepcopy(spec_bundle.language)
    language["metadefinitions"]["DEF_OR"]["rhs"] = {
        "op": "or", "left": {"meta": "P"}, "right": {"meta": "Q"}
    }
    mutated = type(spec_bundle)(
        spec_bundle.spec_dir, language, spec_bundle.rules, spec_bundle.schemas, spec_bundle.systems
    )
    issues = validate_bundle(mutated)
    assert any(i.code == "DEFINITION_CYCLE" for i in issues)


def test_validator_rejects_definition_metavariable_mismatch(spec_bundle):
    language = copy.deepcopy(spec_bundle.language)
    language["metadefinitions"]["DEF_OR"]["rhs"]["arg"]["right"]["arg"] = {"meta": "R"}
    mutated = type(spec_bundle)(
        spec_bundle.spec_dir, language, spec_bundle.rules, spec_bundle.schemas, spec_bundle.systems
    )
    issues = validate_bundle(mutated)
    assert any(i.code == "DEFINITION_METAVARS" for i in issues)
