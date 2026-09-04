import copy

from scripts.validate_spec import EXPECTED_JUSTIFICATION_FIELDS, validate_bundle


def mutate_bundle(spec_bundle, *, rules=None, systems=None, language=None, schemas=None):
    return type(spec_bundle)(
        spec_bundle.spec_dir,
        language or spec_bundle.language,
        rules or spec_bundle.rules,
        schemas or spec_bundle.schemas,
        systems or spec_bundle.systems,
    )


def test_closed_world_top_level(spec_bundle):
    ser = spec_bundle.rules["certificate_serialization"]
    assert ser["closed_world"] is True
    assert ser["unknown_fields_policy"] == "reject"
    assert ser["top_level"]["required_fields"] == ["proof_id", "system", "basis_id", "goal", "root", "nodes"]
    assert ser["top_level"]["allowed_fields"] == ser["top_level"]["required_fields"]


def test_nonempty_string_reference_contract(spec_bundle):
    ids = spec_bundle.rules["certificate_serialization"]["node_id_policy"]
    assert ids["mapping_keys_must_be"] == "nonempty_string"
    assert ids["root_must_be"] == "nonempty_string"
    assert ids["parent_references_must_be"] == "nonempty_string"
    assert ids["reference_resolution"] == "exact_string_identity_no_numeric_or_text_coercion"


def test_each_justification_kind_has_exact_allowed_fields(spec_bundle):
    rules = spec_bundle.rules
    for kind, expected in EXPECTED_JUSTIFICATION_FIELDS.items():
        if kind in {"Sa", "Sb", "Ad", "Smp"}:
            contract = rules["primitive_rules"][kind]["certificate_contract"]
        else:
            contract = rules["kernel_certificate_kinds"][kind]
        assert contract["required_fields"] == expected
        assert contract["allowed_fields"] == expected
        assert contract["unknown_fields_policy"] == "reject"


def test_mutation_unknown_justification_fields_ignored_is_rejected(spec_bundle):
    rules = copy.deepcopy(spec_bundle.rules)
    rules["proof_node_grammar"]["justification_unknown_fields_policy"] = "ignore"
    mutated = mutate_bundle(spec_bundle, rules=rules)
    issues = validate_bundle(mutated, freeze=True)
    assert any(i.code == "JUSTIFICATION_UNKNOWN" for i in issues)


def test_mutation_integer_reference_policy_is_rejected(spec_bundle):
    rules = copy.deepcopy(spec_bundle.rules)
    rules["certificate_serialization"]["node_id_policy"]["parent_references_must_be"] = "string_or_integer"
    mutated = mutate_bundle(spec_bundle, rules=rules)
    issues = validate_bundle(mutated, freeze=True)
    assert any(i.code == "ID_TYPES" for i in issues)
