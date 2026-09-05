from pathlib import Path
import shutil
import sys
import yaml

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_spec import load_spec_bundle


@pytest.fixture(scope="session")
def repo_root():
    return REPO_ROOT


@pytest.fixture(scope="session")
def spec_dir(repo_root):
    return repo_root / "spec"


@pytest.fixture(scope="session")
def spec_bundle(spec_dir):
    return load_spec_bundle(spec_dir)


@pytest.fixture
def copied_candidate(tmp_path, repo_root):
    shutil.copytree(repo_root / "spec", tmp_path / "spec")
    shutil.copytree(repo_root / "audit/m0", tmp_path / "audit/m0")

    # Freeze-mode source validation checks that registered literature paths exist.
    reg = yaml.safe_load((tmp_path / "audit/m0/source_register.yaml").read_text(encoding="utf-8"))
    paths = [reg["canonical_source"]["repository_path"]]
    for entry in reg.get("secondary_sources", {}).values():
        if isinstance(entry, dict) and entry.get("repository_path"):
            paths.append(entry["repository_path"])
    for rel in paths:
        p = tmp_path / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text("test fixture placeholder\n", encoding="utf-8")
    return tmp_path
