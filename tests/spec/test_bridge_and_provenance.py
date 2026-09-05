import copy
import yaml

from scripts.validate_source_register import validate_source_register
from scripts.validate_spec import validate_bundle


PRIMARY = "S5_PRIMARY_B1_B7_C11"
ALT = "S5_ALT_B1_B7_C10_C12"


def test_bridge_orientation_unchanged(spec_bundle):
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


def test_bridge_orientation_mutation_still_rejected(spec_bundle):
    systems = copy.deepcopy(spec_bundle.systems)
    obs = {x["id"]: x for x in systems["systems"]["S5"]["bridge_obligations"]}
    ob = obs["C10_C12_DERIVE_C11"]
    ob["from_basis_id"], ob["into_basis_id"] = ob["into_basis_id"], ob["from_basis_id"]
    ob["expanded_certificate_basis_id"] = ob["into_basis_id"]
    mutated = type(spec_bundle)(
        spec_bundle.spec_dir, spec_bundle.language, spec_bundle.rules, spec_bundle.schemas, systems
    )
    issues = validate_bundle(mutated, freeze=True)
    assert any(i.code == "BRIDGE_DIRECTION" for i in issues)


def test_source_register_normal_and_freeze(repo_root):
    for freeze in (False, True):
        issues = validate_source_register(
            spec_dir=repo_root / "spec",
            register_path=repo_root / "audit/m0/source_register.yaml",
            obligations_path=repo_root / "audit/m0/foundational_obligations.yaml",
            freeze=freeze,
        )
        assert issues == ()


def test_certificate_authority_registered_once(repo_root):
    reg = yaml.safe_load((repo_root / "audit/m0/source_register.yaml").read_text(encoding="utf-8"))
    cc = reg["certificate_contract"]
    assert cc["authoritative_path"] == "spec/rules.yaml#canonical_certificate_contract"
    assert cc["duplicate_machine_readable_semantics_allowed"] is False
    assert cc["human_documentation_status"] == "nonnormative_rendering_of_canonical_contract"


def test_post_certification_status_transition_passes(copied_candidate):
    reg_path = copied_candidate / "audit/m0/source_register.yaml"
    obl_path = copied_candidate / "audit/m0/foundational_obligations.yaml"

    reg = yaml.safe_load(reg_path.read_text(encoding="utf-8"))
    reg["status"] = "frozen_source_audit"
    reg["certificate_contract"]["status"] = "closed"
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
