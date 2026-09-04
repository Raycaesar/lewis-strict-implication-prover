import copy

from scripts.validate_spec import (
    EXPECTED_BASIS_IDS,
    EXPECTED_RESOLVED_BASES,
    EXPECTED_S5_ALTERNATIVE,
    resolve_basis,
    validate_bundle,
)


def test_resolved_primary_bases(spec_bundle):
    systems = spec_bundle.systems["systems"]
    for sid, expected in EXPECTED_RESOLVED_BASES.items():
        assert resolve_basis(systems, sid) == expected


def test_s5_alternative_basis(spec_bundle):
    assert resolve_basis(spec_bundle.systems["systems"], "S5", alternative=True) == EXPECTED_S5_ALTERNATIVE


def test_basis_ids_are_stable(spec_bundle):
    systems = spec_bundle.systems["systems"]
    assert systems["S1"]["normalized_basis"]["basis_id"] == EXPECTED_BASIS_IDS["S1"][0]
    assert systems["S2"]["normalized_basis"]["basis_id"] == EXPECTED_BASIS_IDS["S2"][0]
    assert systems["S3"]["normalized_basis"]["basis_id"] == EXPECTED_BASIS_IDS["S3"][0]
    assert systems["S4"]["normalized_basis"]["basis_id"] == EXPECTED_BASIS_IDS["S4"][0]
    assert systems["S5"]["primary_normalized_basis"]["basis_id"] == EXPECTED_BASIS_IDS["S5"][0]
    assert systems["S5"]["alternative_normalized_basis"]["basis_id"] == EXPECTED_BASIS_IDS["S5"][1]


def test_s5_union_is_forbidden(spec_bundle):
    policy = spec_bundle.systems["systems"]["S5"]["proof_basis_policy"]
    assert policy["union_forbidden"] is True
    assert policy["ui_default"] == "S5_PRIMARY_B1_B7_C11"


def test_every_proof_requires_basis_id(spec_bundle):
    assert spec_bundle.systems["certificate_basis_policy"]["basis_id_required_for_every_proof"] is True


def test_validator_rejects_s5_basis_id_collision(spec_bundle):
    systems = copy.deepcopy(spec_bundle.systems)
    systems["systems"]["S5"]["alternative_normalized_basis"]["basis_id"] = "S5_PRIMARY_B1_B7_C11"
    mutated = type(spec_bundle)(
        spec_bundle.spec_dir, spec_bundle.language, spec_bundle.rules, spec_bundle.schemas, systems
    )
    issues = validate_bundle(mutated)
    assert any(i.code == "S5_ALT_ID" for i in issues)
