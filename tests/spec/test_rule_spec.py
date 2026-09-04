import copy

from scripts.validate_spec import EXPECTED_CERTIFICATE_KINDS, validate_bundle


def test_exact_primitive_rule_registry(spec_bundle):
    assert set(spec_bundle.rules["primitive_rules"]) == {"Sa", "Sb", "Ad", "Smp"}


def test_exact_trusted_certificate_kinds(spec_bundle):
    assert set(spec_bundle.rules["kernel_certificate_kinds"]) == set(EXPECTED_CERTIFICATE_KINDS)


def test_definition_conversion_is_not_lewis_rule(spec_bundle):
    dc = spec_bundle.rules["kernel_certificate_kinds"]["definition_conversion"]
    assert dc["trusted_kind"] is True
    assert dc["is_lewis_inference_rule"] is False
    assert dc["direction_values"] == ["expand", "contract"]


def test_postulate_instance_and_sa_namespaces_are_distinct(spec_bundle):
    post = spec_bundle.rules["kernel_certificate_kinds"]["postulate_instance"]
    sa = spec_bundle.rules["primitive_rules"]["Sa"]["certificate_contract"]["atom_substitution"]
    assert "schema metavariables" in post["schema_substitution"]["key_namespace"]
    assert "object atom" in sa["key_namespace"]
    assert sa["application"] == "simultaneous, one-pass, nonrecursive into replacement values"


def test_occurrence_path_grammar_is_frozen(spec_bundle):
    path = spec_bundle.rules["occurrence_path_grammar"]
    assert path["root"] == []
    assert path["legal_segments"] == ["arg", "left", "right"]
    assert "atom.name" in " ".join(path["reject"])


def test_sb_requires_exact_surface_equiv_s(spec_bundle):
    constraints = " ".join(spec_bundle.rules["primitive_rules"]["Sb"]["constraints"])
    assert "exact visible/surface root equiv_s" in constraints
    assert "No implicit definition conversion" in constraints


def test_smp_uses_exact_surface_antecedent(spec_bundle):
    constraints = " ".join(spec_bundle.rules["primitive_rules"]["Smp"]["constraints"])
    assert "structurally identical" in constraints
    assert "No implicit definition conversion" in constraints


def test_validator_rejects_bad_path_grammar(spec_bundle):
    rules = copy.deepcopy(spec_bundle.rules)
    rules["occurrence_path_grammar"]["legal_segments"] = ["left", "right", "name"]
    mutated = type(spec_bundle)(
        spec_bundle.spec_dir, spec_bundle.language, rules, spec_bundle.schemas, spec_bundle.systems
    )
    issues = validate_bundle(mutated)
    assert any(i.code == "PATH_GRAMMAR" for i in issues)


def test_validator_rejects_missing_definition_conversion_kind(spec_bundle):
    rules = copy.deepcopy(spec_bundle.rules)
    del rules["kernel_certificate_kinds"]["definition_conversion"]
    mutated = type(spec_bundle)(
        spec_bundle.spec_dir, spec_bundle.language, rules, spec_bundle.schemas, spec_bundle.systems
    )
    issues = validate_bundle(mutated)
    assert any(i.code == "CERTIFICATE_KINDS" for i in issues)
