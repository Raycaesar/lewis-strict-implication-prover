import copy
from pathlib import Path

import pytest

from scripts.validate_spec import ValidationError, load_yaml_mapping, validate_spec_dir


def test_current_spec_passes_normal_mode(spec_dir):
    validate_spec_dir(spec_dir)


def test_current_spec_passes_freeze_readiness(spec_dir):
    validate_spec_dir(spec_dir, freeze=True)


def test_duplicate_yaml_keys_rejected(tmp_path):
    path = tmp_path / "dup.yaml"
    path.write_text("x: 1\nx: 2\n", encoding="utf-8")
    with pytest.raises(ValidationError) as exc:
        load_yaml_mapping(path)
    assert any(i.code == "YAML_DUPLICATE_KEY" for i in exc.value.issues)


def test_missing_required_spec_files_reported(tmp_path):
    with pytest.raises(ValidationError) as exc:
        validate_spec_dir(tmp_path)
    assert any(i.code == "FILE_MISSING" for i in exc.value.issues)
