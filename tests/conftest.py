from pathlib import Path
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
