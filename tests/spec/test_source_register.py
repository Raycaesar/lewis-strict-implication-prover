from pathlib import Path
import shutil
import yaml

from scripts.validate_source_register import validate_source_register
from scripts.validate_spec import StrictLoader


def test_source_register_matches_spec(repo_root):
    issues = validate_source_register(
        spec_dir=repo_root / "spec",
        register_path=repo_root / "audit/m0/source_register.yaml",
        obligations_path=repo_root / "audit/m0/foundational_obligations.yaml",
    )
    assert issues == ()


def test_source_register_freeze_readiness(repo_root):
    issues = validate_source_register(
        spec_dir=repo_root / "spec",
        register_path=repo_root / "audit/m0/source_register.yaml",
        obligations_path=repo_root / "audit/m0/foundational_obligations.yaml",
        freeze=True,
    )
    assert issues == ()


def test_no_unresolved_blocked_open_or_repair_needed_statuses(repo_root):
    data = yaml.load(
        (repo_root / "audit/m0/foundational_obligations.yaml").read_text(encoding="utf-8"),
        Loader=StrictLoader,
    )
    bad = {"blocked", "open", "repair_needed"}
    assert not [
        oid for oid, item in data["obligations"].items() if item.get("status") in bad
    ]


def test_first_audit_repairs_are_explicitly_pending_reaudit(repo_root):
    data = yaml.load(
        (repo_root / "audit/m0/foundational_obligations.yaml").read_text(encoding="utf-8"),
        Loader=StrictLoader,
    )
    for oid in ("M0-D03", "M0-D04", "M0-C01", "M0-C02", "M0-C03", "M0-C04"):
        assert data["obligations"][oid]["status"] == "repair_implemented_reaudit_pending"
