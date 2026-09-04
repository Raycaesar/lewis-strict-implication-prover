from scripts.validate_spec import (
    EXPECTED_RESOLVED_BASES,
    EXPECTED_S5_ALTERNATIVE,
    EXPECTED_SYSTEMS,
    resolve_basis,
)


def test_system_registry_is_exact(spec_bundle):
    assert set(spec_bundle.systems["systems"]) == set(EXPECTED_SYSTEMS)


def test_primary_normalized_bases_resolve_exactly(spec_bundle):
    systems = spec_bundle.systems["systems"]
    for system_id, expected in EXPECTED_RESOLVED_BASES.items():
        assert resolve_basis(systems, system_id) == expected


def test_s5_alternative_basis_resolves_exactly(spec_bundle):
    systems = spec_bundle.systems["systems"]
    assert resolve_basis(systems, "S5", alternative=True) == EXPECTED_S5_ALTERNATIVE


def test_every_system_uses_only_the_four_primitive_rules(spec_bundle):
    systems = spec_bundle.systems["systems"]
    expected = {"Sa", "Sb", "Ad", "Smp"}

    for system_id in ("S1", "S2", "S3", "S4"):
        assert set(systems[system_id]["normalized_basis"]["rules"]) == expected

    assert set(systems["S5"]["primary_normalized_basis"]["rules"]) == expected
    assert set(systems["S5"]["alternative_normalized_basis"]["rules"]) == expected


def test_theorem_inclusion_is_not_kernel_trusted(spec_bundle):
    inclusion = spec_bundle.systems["theorem_inclusion"]
    assert inclusion["trusted_by_kernel_without_bridge"] is False


def test_b9_extension_is_disabled(spec_bundle):
    b9 = spec_bundle.systems["extensions_not_in_m0"]["B9_existence"]
    assert b9["enabled"] is False
