import copy

from scripts.validate_spec import validate_bundle


def mb(spec_bundle, *, rules=None, systems=None):
    return type(spec_bundle)(
        spec_bundle.spec_dir,
        spec_bundle.language,
        rules or spec_bundle.rules,
        spec_bundle.schemas,
        systems or spec_bundle.systems,
    )


def test_mutation_postulate_missing_keys_allowed_fails(spec_bundle):
    rules = copy.deepcopy(spec_bundle.rules)
    post = rules["kernel_certificate_kinds"]["postulate_instance"]["schema_substitution"]
    post["domain_policy"] = "subset_schema_metavariables"
    post["missing_keys_policy"] = "allow"
    issues = validate_bundle(mb(spec_bundle, rules=rules), freeze=True)
    assert any(i.code in {"POST_DOMAIN", "POST_KEYS"} for i in issues)


def test_mutation_definition_independent_environments_fails(spec_bundle):
    rules = copy.deepcopy(spec_bundle.rules)
    dc = rules["kernel_certificate_kinds"]["definition_conversion"]
    dc["metavariable_environment_policy"] = "independent_environment_per_occurrence"
    issues = validate_bundle(mb(spec_bundle, rules=rules), freeze=True)
    assert any(i.code == "DF_ENV" for i in issues)


def test_mutation_definition_second_conversion_allowed_fails(spec_bundle):
    rules = copy.deepcopy(spec_bundle.rules)
    dc = rules["kernel_certificate_kinds"]["definition_conversion"]
    dc["implicit_additional_conversion"] = "allow"
    issues = validate_bundle(mb(spec_bundle, rules=rules), freeze=True)
    assert any(i.code == "DF_SECOND" for i in issues)


def test_mutation_sb_multiple_replacements_fails(spec_bundle):
    rules = copy.deepcopy(spec_bundle.rules)
    rules["primitive_rules"]["Sb"]["certificate_contract"]["replacement_count"] = "one_or_more"
    issues = validate_bundle(mb(spec_bundle, rules=rules), freeze=True)
    assert any(i.code == "SB_COUNT" for i in issues)


def test_mutation_atom_name_traversable_fails(spec_bundle):
    rules = copy.deepcopy(spec_bundle.rules)
    rules["occurrence_path_grammar"]["atom_traversable_fields"] = ["name"]
    issues = validate_bundle(mb(spec_bundle, rules=rules), freeze=True)
    assert any(i.code == "ATOM_PATH" for i in issues)


def test_mutation_s5_bridge_orientation_swapped_fails(spec_bundle):
    systems = copy.deepcopy(spec_bundle.systems)
    obs = {x["id"]: x for x in systems["systems"]["S5"]["bridge_obligations"]}
    ob = obs["C10_C12_DERIVE_C11"]
    ob["from_basis_id"], ob["into_basis_id"] = ob["into_basis_id"], ob["from_basis_id"]
    ob["expanded_certificate_basis_id"] = ob["into_basis_id"]
    issues = validate_bundle(mb(spec_bundle, systems=systems), freeze=True)
    assert any(i.code == "BRIDGE_DIRECTION" for i in issues)


def test_mutation_unknown_fields_policy_ignore_fails(spec_bundle):
    rules = copy.deepcopy(spec_bundle.rules)
    rules["certificate_serialization"]["unknown_fields_policy"] = "ignore"
    issues = validate_bundle(mb(spec_bundle, rules=rules), freeze=True)
    assert any(i.code == "CLOSED_WORLD" for i in issues)
