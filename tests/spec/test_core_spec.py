from scripts.validate_spec import (
    EXPECTED_AST_OPS,
    EXPECTED_CERTIFICATE_KINDS,
    EXPECTED_SCHEMA_IDS,
    EXPECTED_RESOLVED_BASES,
    EXPECTED_S5_ALTERNATIVE,
    resolve_basis,
    validate_spec_dir,
)


def test_candidate_passes_normal_validation(spec_dir):
    validate_spec_dir(spec_dir)


def test_candidate_passes_freeze_validation(spec_dir):
    validate_spec_dir(spec_dir, freeze=True)


def test_ast_registry_exact(spec_bundle):
    assert set(spec_bundle.language["formula_ast"]) == set(EXPECTED_AST_OPS)


def test_schema_registry_exact(spec_bundle):
    assert set(spec_bundle.schemas["schemas"]) == set(EXPECTED_SCHEMA_IDS)


def test_trusted_certificate_kinds_exact(spec_bundle):
    assert set(spec_bundle.rules["kernel_certificate_kinds"]) == set(EXPECTED_CERTIFICATE_KINDS)


def test_normalized_bases_unchanged(spec_bundle):
    systems = spec_bundle.systems["systems"]
    for sid, expected in EXPECTED_RESOLVED_BASES.items():
        assert resolve_basis(systems, sid) == expected
    assert resolve_basis(systems, "S5", alternative=True) == EXPECTED_S5_ALTERNATIVE


def test_no_box_b9_or_unrestricted_necessitation(spec_bundle):
    assert "box" not in spec_bundle.language["formula_ast"]
    assert spec_bundle.systems["extensions_not_in_m0"]["B9_existence"]["enabled"] is False
    assert spec_bundle.rules["explicitly_forbidden_rules"]["unrestricted_necessitation"]["enabled"] is False
