import copy
import hashlib
import json
import yaml

from scripts.validate_spec import validate_bundle


def mb(spec_bundle, rules):
    return type(spec_bundle)(
        spec_bundle.spec_dir,
        spec_bundle.language,
        rules,
        spec_bundle.schemas,
        spec_bundle.systems,
    )


def test_contract_lock_matches_current_canonical_contract(repo_root, spec_bundle):
    lock = yaml.safe_load(
        (repo_root / "audit/m0/certificate_contract_lock.yaml").read_text(encoding="utf-8")
    )
    canonical = json.dumps(
        spec_bundle.rules["canonical_certificate_contract"],
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    )
    actual = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    assert lock["canonical_contract_sha256"] == actual
    assert lock["repair_parent_commit"] == "5f86547a2f16e5f1e1620823e3b68457fb8350b7"


def test_any_canonical_contract_mutation_breaks_freeze_lock(spec_bundle):
    rules = copy.deepcopy(spec_bundle.rules)
    rules["canonical_certificate_contract"]["metadata_policy"] = "allow_metadata"
    issues = validate_bundle(mb(spec_bundle, rules), freeze=True)
    assert any(i.code in {"CONTRACT_METADATA", "FINGERPRINT_CONTRACT"} for i in issues)


def test_existing_ast_fingerprints_still_pass(spec_dir):
    from scripts.validate_spec import validate_spec_dir
    validate_spec_dir(spec_dir, freeze=True)
