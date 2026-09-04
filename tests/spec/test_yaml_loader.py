import pytest

from scripts.validate_spec import ValidationError, load_yaml_mapping


def test_duplicate_yaml_keys_rejected(tmp_path):
    path = tmp_path / "dup.yaml"
    path.write_text("x: 1\nx: 2\n", encoding="utf-8")
    with pytest.raises(ValidationError) as exc:
        load_yaml_mapping(path)
    assert any(i.code == "YAML_DUPLICATE_KEY" for i in exc.value.issues)


def test_missing_file_rejected(tmp_path):
    with pytest.raises(ValidationError) as exc:
        load_yaml_mapping(tmp_path / "missing.yaml")
    assert any(i.code == "FILE_MISSING" for i in exc.value.issues)
