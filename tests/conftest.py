from pathlib import Path
import shutil
import sys

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_spec import load_spec_bundle


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def spec_dir(repo_root: Path) -> Path:
    return repo_root / "spec"


@pytest.fixture(scope="session")
def spec_bundle(spec_dir: Path):
    return load_spec_bundle(spec_dir)


@pytest.fixture
def copied_m0(tmp_path, repo_root):
    shutil.copytree(repo_root / "spec", tmp_path / "spec")
    (tmp_path / "audit/m0").mkdir(parents=True)
    for name in (
        "certified_ast_fingerprints.yaml",
        "source_register.yaml",
        "foundational_obligations.yaml",
    ):
        shutil.copy2(repo_root / "audit/m0" / name, tmp_path / "audit/m0" / name)
    return tmp_path
