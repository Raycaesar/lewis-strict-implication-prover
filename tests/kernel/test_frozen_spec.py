from __future__ import annotations

import shutil

import pytest
import yaml

from lewis_prover.errors import (
    FrozenContractError,
    FrozenSpecBasisError,
    FrozenSpecFingerprintError,
    FrozenSpecFormatError,
    FrozenSpecStatusError,
)
from lewis_prover.kernel import load_frozen_spec


@pytest.fixture
def frozen_copy(tmp_path, repo_root):
    shutil.copytree(repo_root / "spec", tmp_path / "spec")
    (tmp_path / "audit/m0").mkdir(parents=True)
    for filename in ("certified_ast_fingerprints.yaml", "certificate_contract_lock.yaml"):
        shutil.copy2(repo_root / "audit/m0" / filename, tmp_path / "audit/m0" / filename)
    return tmp_path


def _mutate_yaml(path, mutate):
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    mutate(value)
    path.write_text(yaml.safe_dump(value, sort_keys=False, allow_unicode=True), encoding="utf-8")


def test_loads_frozen_spec_as_deeply_read_only(repo_root):
    frozen = load_frozen_spec(repo_root)

    assert frozen.spec_version == "0.6"
    assert frozen.language["status"] == "frozen_m0"
    assert set(frozen.bases) == {
        "S1_B1_B7",
        "S2_B1_B8",
        "S3_B1_B7_A8",
        "S4_B1_B7_C10",
        "S5_PRIMARY_B1_B7_C11",
        "S5_ALT_B1_B7_C10_C12",
    }
    with pytest.raises(TypeError):
        frozen.language["status"] = "candidate_m0"
    with pytest.raises(TypeError):
        frozen.canonical_certificate_contract["closed_world"] = False


def test_rejects_non_frozen_status(frozen_copy):
    path = frozen_copy / "spec/language.yaml"
    _mutate_yaml(path, lambda value: value.__setitem__("status", "candidate_m0"))

    with pytest.raises(FrozenSpecStatusError, match="language.yaml status"):
        load_frozen_spec(frozen_copy)


def test_rejects_altered_schema_fingerprint(frozen_copy):
    path = frozen_copy / "spec/schemas.yaml"
    _mutate_yaml(path, lambda value: value["schemas"]["B1"]["ast"].__setitem__("right", {"meta": "P"}))

    with pytest.raises(FrozenSpecFingerprintError, match="schema AST fingerprint mismatch: B1"):
        load_frozen_spec(frozen_copy)


def test_rejects_altered_definition_fingerprint(frozen_copy):
    path = frozen_copy / "spec/language.yaml"
    _mutate_yaml(
        path,
        lambda value: value["metadefinitions"]["DEF_OR"]["rhs"].__setitem__("arg", {"meta": "P"}),
    )

    with pytest.raises(FrozenSpecFingerprintError, match="definition AST fingerprint mismatch: DEF_OR"):
        load_frozen_spec(frozen_copy)


def test_rejects_altered_canonical_contract(frozen_copy):
    path = frozen_copy / "spec/rules.yaml"
    _mutate_yaml(
        path,
        lambda value: value["canonical_certificate_contract"].__setitem__("closed_world", False),
    )

    with pytest.raises(FrozenContractError, match="contract fingerprint mismatch"):
        load_frozen_spec(frozen_copy)


def test_rejects_altered_contract_lock(frozen_copy):
    path = frozen_copy / "audit/m0/certificate_contract_lock.yaml"
    _mutate_yaml(path, lambda value: value.__setitem__("canonical_contract_sha256", "0" * 64))

    with pytest.raises(FrozenContractError, match="lock object has changed"):
        load_frozen_spec(frozen_copy)


def test_rejects_s5_basis_id_collision(frozen_copy):
    path = frozen_copy / "spec/systems.yaml"

    def collide(value):
        primary = value["systems"]["S5"]["primary_normalized_basis"]["basis_id"]
        value["systems"]["S5"]["alternative_normalized_basis"]["basis_id"] = primary

    _mutate_yaml(path, collide)
    with pytest.raises(FrozenSpecBasisError, match="basis ID mismatch"):
        load_frozen_spec(frozen_copy)


@pytest.mark.parametrize(
    "mutation",
    [
        lambda value: value["systems"]["S5"]["primary_normalized_basis"]["add_schemas"].append("C10"),
        lambda value: value["systems"]["S5"]["alternative_normalized_basis"]["add_schemas"].append("C11"),
        lambda value: value["systems"]["S5"]["proof_basis_policy"].__setitem__("union_forbidden", False),
    ],
)
def test_rejects_s5_basis_union(frozen_copy, mutation):
    path = frozen_copy / "spec/systems.yaml"
    _mutate_yaml(path, mutation)

    with pytest.raises(FrozenSpecBasisError):
        load_frozen_spec(frozen_copy)


def test_rejects_duplicate_yaml_keys(frozen_copy):
    path = frozen_copy / "spec/language.yaml"
    path.write_text(path.read_text(encoding="utf-8") + "\nstatus: frozen_m0\n", encoding="utf-8")

    with pytest.raises(FrozenSpecFormatError, match="duplicate YAML key 'status'"):
        load_frozen_spec(frozen_copy)
