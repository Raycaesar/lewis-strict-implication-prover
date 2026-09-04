import copy
from pathlib import Path

import yaml

from scripts.validate_source_register import validate_source_register
from scripts.validate_spec import StrictLoader, validate_bundle


PRIMARY = "S5_PRIMARY_B1_B7_C11"
ALT = "S5_ALT_B1_B7_C10_C12"


def test_bridge_direction_is_operational(spec_bundle):
    obs = {x["id"]: x for x in spec_bundle.systems["systems"]["S5"]["bridge_obligations"]}
    a = obs["C10_C12_DERIVE_C11"]
    assert a["from_basis_id"] == PRIMARY
    assert a["into_basis_id"] == ALT
    assert a["recovered_primitive_schemas"] == ["C11"]
    assert a["expanded_certificate_basis_id"] == ALT

    b = obs["C11_DERIVES_C10_C12"]
    assert b["from_basis_id"] == ALT
    assert b["into_basis_id"] == PRIMARY
    assert b["recovered_primitive_schemas"] == ["C10", "C12"]
    assert b["expanded_certificate_basis_id"] == PRIMARY


def test_no_legacy_source_target_bridge_fields(spec_bundle):
    for ob in spec_bundle.systems["systems"]["S5"]["bridge_obligations"]:
        assert "source_basis_id" not in ob
        assert "target_basis_id" not in ob


def test_source_register_normal_validation(repo_root):
    issues = validate_source_register(
        spec_dir=repo_root / "spec",
        register_path=repo_root / "audit/m0/source_register.yaml",
        obligations_path=repo_root / "audit/m0/foundational_obligations.yaml",
    )
    assert issues == ()


def test_source_register_freeze_validation(repo_root):
    issues = validate_source_register(
        spec_dir=repo_root / "spec",
        register_path=repo_root / "audit/m0/source_register.yaml",
        obligations_path=repo_root / "audit/m0/foundational_obligations.yaml",
        freeze=True,
    )
    assert issues == ()


def test_all_active_parry_fields_use_precise_reduced_list(repo_root):
    reg = yaml.load(
        (repo_root / "audit/m0/source_register.yaml").read_text(encoding="utf-8"),
        Loader=StrictLoader,
    )
    systems = yaml.load((repo_root / "spec/systems.yaml").read_text(encoding="utf-8"), Loader=StrictLoader)
    schemas = yaml.load((repo_root / "spec/schemas.yaml").read_text(encoding="utf-8"), Loader=StrictLoader)

    texts = [
        reg["secondary_sources"]["PARRY1939"]["use"][0],
        reg["primitive_schemas"]["A8"]["parry_crosscheck"],
        reg["normalized_systems"]["S3"]["normalized_basis_support"]["statement"],
        systems["normalization_policy"]["key_decisions"][2],
        systems["systems"]["S3"]["historical_basis_note"],
        schemas["schema_policy"]["explanation"][2],
        schemas["schemas"]["A8"]["normalization_note"],
    ]
    for text in texts:
        for token in ("11.1-11.4", "11.6", "11.7", "30.1/A8", "11.5", "McKinsey"):
            assert token in text
        assert "11.1-11.7 plus 30.1/A8" not in text
        assert "11.1-11.7 together with 30.1/A8 as postulates" not in text



def test_parry_provenance_mutation_is_rejected(copied_candidate):
    schemas_path = copied_candidate / "spec/schemas.yaml"
    schemas = yaml.safe_load(schemas_path.read_text(encoding="utf-8"))
    schemas["schema_policy"]["explanation"][2] = (
        "Parry explicitly uses 11.1-11.7 together with 30.1/A8 as postulates for S3."
    )
    schemas_path.write_text(yaml.safe_dump(schemas, sort_keys=False), encoding="utf-8")

    issues = validate_source_register(
        spec_dir=copied_candidate / "spec",
        register_path=copied_candidate / "audit/m0/source_register.yaml",
        obligations_path=copied_candidate / "audit/m0/foundational_obligations.yaml",
        freeze=True,
    )
    assert any(i.code in {"PARRY_INCOMPLETE", "PARRY_INACCURATE"} for i in issues)


def test_post_certification_closed_status_transition_passes(copied_candidate):
    reg_path = copied_candidate / "audit/m0/source_register.yaml"
    obl_path = copied_candidate / "audit/m0/foundational_obligations.yaml"

    reg = yaml.safe_load(reg_path.read_text(encoding="utf-8"))
    reg["status"] = "frozen_source_audit"
    reg_path.write_text(yaml.safe_dump(reg, sort_keys=False), encoding="utf-8")

    obligations = yaml.safe_load(obl_path.read_text(encoding="utf-8"))
    for item in obligations["obligations"].values():
        if item.get("status") == "repair_implemented_reaudit_pending":
            item["status"] = "closed"
    obl_path.write_text(yaml.safe_dump(obligations, sort_keys=False), encoding="utf-8")

    issues = validate_source_register(
        spec_dir=copied_candidate / "spec",
        register_path=reg_path,
        obligations_path=obl_path,
        freeze=True,
    )
    assert issues == ()
