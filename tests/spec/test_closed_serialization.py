import copy

from scripts.validate_spec import (
    EXPECTED_KIND_FIELDS,
    EXPECTED_NODE_FIELDS,
    EXPECTED_TOP_LEVEL_CERT_FIELDS,
    validate_bundle,
)


def mutated(spec_bundle, rules):
    return type(spec_bundle)(
        spec_bundle.spec_dir,
        spec_bundle.language,
        rules,
        spec_bundle.schemas,
        spec_bundle.systems,
    )


def test_single_machine_readable_contract_authority(spec_bundle):
    rules = spec_bundle.rules
    assert rules["canonical_certificate_contract"]["authority"] == "sole_machine_readable_certificate_authority"
    for legacy in (
        "primitive_rules",
        "kernel_certificate_kinds",
        "occurrence_path_grammar",
        "proof_node_grammar",
        "dag_invariants",
        "certificate_serialization",
        "trusted_kernel_invariant",
    ):
        assert legacy not in rules


def test_top_and_node_closed_world(spec_bundle):
    c = spec_bundle.rules["canonical_certificate_contract"]
    assert c["top_level"]["required_fields"] == EXPECTED_TOP_LEVEL_CERT_FIELDS
    assert c["top_level"]["allowed_fields"] == EXPECTED_TOP_LEVEL_CERT_FIELDS
    assert c["top_level"]["unknown_fields_policy"] == "reject"
    assert c["node"]["required_fields"] == EXPECTED_NODE_FIELDS
    assert c["node"]["allowed_fields"] == EXPECTED_NODE_FIELDS
    assert c["node"]["unknown_fields_policy"] == "reject"


def test_every_kind_has_exact_fields(spec_bundle):
    kinds = spec_bundle.rules["canonical_certificate_contract"]["kinds"]
    for kind, fields in EXPECTED_KIND_FIELDS.items():
        assert kinds[kind]["required_fields"] == fields
        assert kinds[kind]["allowed_fields"] == fields
        assert kinds[kind]["unknown_fields_policy"] == "reject"


def test_legacy_duplicate_semantic_registry_injection_is_rejected(spec_bundle):
    for legacy in (
        "primitive_rules",
        "kernel_certificate_kinds",
        "occurrence_path_grammar",
        "proof_node_grammar",
        "dag_invariants",
        "certificate_serialization",
        "trusted_kernel_invariant",
    ):
        rules = copy.deepcopy(spec_bundle.rules)
        rules[legacy] = {"contradictory": "semantic mirror"}
        issues = validate_bundle(mutated(spec_bundle, rules), freeze=True)
        assert any(i.code in {"RULES_TOPLEVEL_KEYS", "LEGACY_RULES_SEMANTICS"} for i in issues), legacy


def test_lewis_operations_cannot_hide_semantics(spec_bundle):
    rules = copy.deepcopy(spec_bundle.rules)
    rules["lewis_operations"]["Sa"]["constraints"] = ["extra executable semantics"]
    issues = validate_bundle(mutated(spec_bundle, rules), freeze=True)
    assert any(i.code == "LEWIS_OPERATION_FIELDS" for i in issues)
