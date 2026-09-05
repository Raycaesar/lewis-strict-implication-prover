from scripts.validate_spec import (
    EXPECTED_AST_OPS,
    EXPECTED_CERTIFICATE_KINDS,
    EXPECTED_RESOLVED_BASES,
    EXPECTED_SCHEMA_IDS,
    EXPECTED_S5_ALTERNATIVE,
    resolve_basis,
    validate_spec_dir,
)


def test_candidate_passes_normal_validation(spec_dir):
    validate_spec_dir(spec_dir)


def test_candidate_passes_freeze_validation(spec_dir):
    validate_spec_dir(spec_dir, freeze=True)


def test_formula_registry_unchanged(spec_bundle):
    assert set(spec_bundle.language["formula_ast"]) == set(EXPECTED_AST_OPS)
    assert set(spec_bundle.schemas["schemas"]) == set(EXPECTED_SCHEMA_IDS)


def test_normalized_bases_unchanged(spec_bundle):
    systems = spec_bundle.systems["systems"]
    for sid, expected in EXPECTED_RESOLVED_BASES.items():
        assert resolve_basis(systems, sid) == expected
    assert resolve_basis(systems, "S5", alternative=True) == EXPECTED_S5_ALTERNATIVE


def test_canonical_certificate_kind_set(spec_bundle):
    kinds = spec_bundle.rules["canonical_certificate_contract"]["kinds"]
    assert tuple(kinds) == tuple(EXPECTED_CERTIFICATE_KINDS)


def test_no_forbidden_m0_extensions(spec_bundle):
    assert "box" not in spec_bundle.language["formula_ast"]
    assert spec_bundle.systems["extensions_not_in_m0"]["B9_existence"]["enabled"] is False
    assert spec_bundle.rules["explicitly_forbidden_rules"]["unrestricted_necessitation"]["enabled"] is False



def test_post_certification_spec_status_transition_passes(copied_candidate):
    import yaml
    from scripts.validate_spec import validate_spec_dir

    for name in ("language", "rules", "schemas", "systems"):
        path = copied_candidate / "spec" / f"{name}.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        data["status"] = "frozen_m0"
        path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")

    validate_spec_dir(copied_candidate / "spec", freeze=True)
