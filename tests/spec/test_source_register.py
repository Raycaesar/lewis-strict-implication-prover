from pathlib import Path

from scripts.validate_source_register import validate_source_register


def test_source_register_matches_executable_spec(repo_root):
    issues = validate_source_register(
        spec_dir=repo_root / "spec",
        register_path=repo_root / "audit/m0/source_register.yaml",
        obligations_path=repo_root / "audit/m0/foundational_obligations.yaml",
    )
    assert issues == ()


def test_source_register_has_exact_primitive_schema_coverage(repo_root):
    import yaml
    from scripts.validate_spec import StrictLoader, EXPECTED_SCHEMA_IDS

    path = repo_root / "audit/m0/source_register.yaml"
    data = yaml.load(path.read_text(encoding="utf-8"), Loader=StrictLoader)
    assert set(data["primitive_schemas"]) == set(EXPECTED_SCHEMA_IDS)


def test_source_register_marks_sa_sb_as_project_labels(repo_root):
    import yaml
    from scripts.validate_spec import StrictLoader

    path = repo_root / "audit/m0/source_register.yaml"
    data = yaml.load(path.read_text(encoding="utf-8"), Loader=StrictLoader)
    assert data["primitive_operations"]["Sa"]["project_label"] == "Sa"
    assert data["primitive_operations"]["Sb"]["project_label"] == "Sb"
    assert "historical_label" not in data["primitive_operations"]["Sa"]
    assert "historical_label" not in data["primitive_operations"]["Sb"]


def test_freeze_register_contains_explicit_blockers(repo_root):
    import yaml
    from scripts.validate_spec import StrictLoader

    path = repo_root / "audit/m0/foundational_obligations.yaml"
    data = yaml.load(path.read_text(encoding="utf-8"), Loader=StrictLoader)
    blockers = [
        oid
        for oid, item in data["obligations"].items()
        if item.get("status") == "blocked"
    ]
    assert {"M0-D03", "M0-D04", "M0-C01"} <= set(blockers)
