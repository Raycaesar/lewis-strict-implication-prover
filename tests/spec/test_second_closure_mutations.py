import copy

from scripts.validate_spec import validate_bundle


def mb(spec_bundle, rules):
    return type(spec_bundle)(
        spec_bundle.spec_dir,
        spec_bundle.language,
        rules,
        spec_bundle.schemas,
        spec_bundle.systems,
    )


def freeze_codes(spec_bundle, mutate):
    rules = copy.deepcopy(spec_bundle.rules)
    mutate(rules["canonical_certificate_contract"])
    return {i.code for i in validate_bundle(mb(spec_bundle, rules), freeze=True)}


# Five semantic mutations that M0.4 accepted through old duplicated fields.

def test_replay_postulate_missing_keys_mutation_rejected(spec_bundle):
    codes = freeze_codes(
        spec_bundle,
        lambda c: c["kinds"]["postulate_instance"]["schema_substitution"].update(
            domain_policy="subset_schema_metavariables",
            missing_keys_policy="allow",
        ),
    )
    assert "POSTULATE_SUBSTITUTION" in codes or "FINGERPRINT_CONTRACT" in codes


def test_replay_definition_independent_environment_mutation_rejected(spec_bundle):
    codes = freeze_codes(
        spec_bundle,
        lambda c: c["kinds"]["definition_conversion"].update(
            metavariable_environment_policy="independent_environment_per_occurrence"
        ),
    )
    assert "DF_POLICY" in codes or "FINGERPRINT_CONTRACT" in codes


def test_replay_definition_second_conversion_mutation_rejected(spec_bundle):
    codes = freeze_codes(
        spec_bundle,
        lambda c: c["kinds"]["definition_conversion"].update(
            implicit_additional_conversion="allow"
        ),
    )
    assert "DF_POLICY" in codes or "FINGERPRINT_CONTRACT" in codes


def test_replay_sb_multiple_replacement_mutation_rejected(spec_bundle):
    codes = freeze_codes(
        spec_bundle,
        lambda c: c["kinds"]["Sb"].update(replacement_count="one_or_more"),
    )
    assert "SB_POLICY" in codes or "FINGERPRINT_CONTRACT" in codes


def test_replay_atom_name_traversal_mutation_rejected(spec_bundle):
    codes = freeze_codes(
        spec_bundle,
        lambda c: c["occurrence_path"]["traversable_fields"].update(atom=["name"]),
    )
    assert "CONTRACT_PATH_TRAVERSAL" in codes or "FINGERPRINT_CONTRACT" in codes


# Four additional serialization mutations M0.4 accepted through old mirrors.

def test_replay_node_metadata_field_mutation_rejected(spec_bundle):
    def mutate(c):
        c["node"]["required_fields"].append("metadata")
        c["node"]["allowed_fields"].append("metadata")
    codes = freeze_codes(spec_bundle, mutate)
    assert "CONTRACT_NODE_FIELDS" in codes or "FINGERPRINT_CONTRACT" in codes


def test_replay_node_extra_fields_allowed_mutation_rejected(spec_bundle):
    codes = freeze_codes(
        spec_bundle,
        lambda c: c["node"].update(unknown_fields_policy="allow"),
    )
    assert "CONTRACT_NODE_POLICY" in codes or "FINGERPRINT_CONTRACT" in codes


def test_replay_node_reference_string_or_integer_mutation_rejected(spec_bundle):
    codes = freeze_codes(
        spec_bundle,
        lambda c: c["identifier_policy"].update(parent_reference_type="string_or_integer"),
    )
    assert "CONTRACT_ID_POLICY" in codes or "FINGERPRINT_CONTRACT" in codes


def test_replay_coercive_string_identity_mutation_rejected(spec_bundle):
    codes = freeze_codes(
        spec_bundle,
        lambda c: c["identifier_policy"].update(
            string_identity="coerce_numeric_and_normalize_unicode"
        ),
    )
    assert "CONTRACT_ID_POLICY" in codes or "FINGERPRINT_CONTRACT" in codes


def test_arbitrary_unchecked_contract_field_addition_breaks_freeze_fingerprint(spec_bundle):
    codes = freeze_codes(
        spec_bundle,
        lambda c: c.update(unreviewed_semantic_extension=True),
    )
    assert "FINGERPRINT_CONTRACT" in codes
