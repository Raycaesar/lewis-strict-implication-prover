import pytest

from scripts.validate_spec import ValidationError, load_yaml_mapping, validate_spec_dir


def test_current_repository_spec_passes(spec_dir):
    validate_spec_dir(spec_dir)


def test_duplicate_yaml_keys_are_rejected(tmp_path):
    path = tmp_path / "duplicate.yaml"
    path.write_text("x: 1\nx: 2\n", encoding="utf-8")

    with pytest.raises(ValidationError) as exc_info:
        load_yaml_mapping(path)

    assert any(issue.code == "YAML_DUPLICATE_KEY" for issue in exc_info.value.issues)


def test_missing_required_file_is_reported(tmp_path):
    with pytest.raises(ValidationError) as exc_info:
        validate_spec_dir(tmp_path)

    assert any(issue.code == "FILE_MISSING" for issue in exc_info.value.issues)
