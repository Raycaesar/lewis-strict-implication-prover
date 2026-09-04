import shutil
import yaml

import pytest

from scripts.validate_spec import StrictLoader, ValidationError, validate_spec_dir


def test_fingerprint_metadata_is_locked(repo_root):
    data = yaml.load(
        (repo_root / "audit/m0/certified_ast_fingerprints.yaml").read_text(encoding="utf-8"),
        Loader=StrictLoader,
    )
    assert data["lock_version"] == "0.2"
    assert data["formula_source_audit_commit"] == "4931e4daa124587a789ac27b841f499295facf5e"
    assert data["formula_nonregression_recheck_commit"] == "5339a5a4f4c56a5e4feae3cc452730e488a309f1"


def test_mutated_fingerprint_metadata_fails_freeze(copied_candidate):
    path = copied_candidate / "audit/m0/certified_ast_fingerprints.yaml"
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    data["formula_nonregression_recheck_commit"] = "0" * 40
    path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")

    with pytest.raises(ValidationError) as exc:
        validate_spec_dir(copied_candidate / "spec", freeze=True)
    assert any(i.code == "LOCK_RECHECK_COMMIT" for i in exc.value.issues)
