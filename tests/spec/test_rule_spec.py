EXPECTED = {"Sa", "Sb", "Ad", "Smp"}


def test_primitive_rule_registry_is_exact(spec_bundle):
    assert set(spec_bundle.rules["primitive_rules"]) == EXPECTED


def test_rule_labels_are_stable(spec_bundle):
    for rule_id, rule in spec_bundle.rules["primitive_rules"].items():
        assert rule["historical_label"] == rule_id


def test_unrestricted_necessitation_is_disabled(spec_bundle):
    forbidden = spec_bundle.rules["explicitly_forbidden_rules"]
    assert forbidden["unrestricted_necessitation"]["enabled"] is False


def test_semantic_validity_is_not_a_rule(spec_bundle):
    forbidden = spec_bundle.rules["explicitly_forbidden_rules"]
    assert forbidden["semantic_validity"]["enabled"] is False


def test_definitions_and_system_inclusion_are_not_rules(spec_bundle):
    non_rules = spec_bundle.rules["non_rules"]
    assert non_rules["definition_expansion"]["is_inference_rule"] is False
    assert non_rules["definition_contraction"]["is_inference_rule"] is False
    assert non_rules["system_inclusion"]["is_inference_rule"] is False
