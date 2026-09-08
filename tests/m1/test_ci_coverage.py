"""Keep the M1 validation workflow active for every requested trust surface."""

from fnmatch import fnmatchcase

import pytest
import yaml


SURFACES = (
    "src/lewis_prover/kernel/frozen_spec.py", "src/lewis_prover/syntax/formula.py",
    "src/lewis_prover/cli.py", "tests/kernel/nested/future_test.py",
    "tests/syntax/test_formula.py", "tests/m1/test_cli.py", "tests/fixtures/m1/invalid/new.json",
    "scripts/future_validation.py", "spec/language.yaml", "audit/m0/certificate_contract_lock.yaml",
    "audit/m1/future_reaudit.md", "pyproject.toml", "AGENTS.md", ".github/workflows/future.yml",
)


@pytest.fixture(scope="module")
def workflow(repo_root):
    # BaseLoader preserves GitHub's YAML 'on' key rather than resolving it as a bool.
    return yaml.load((repo_root / ".github/workflows/m1-trusted-kernel-validation.yml").read_bytes(), Loader=yaml.BaseLoader)


@pytest.mark.parametrize("event", ("push", "pull_request"))
@pytest.mark.parametrize("path", SURFACES)
def test_m1_workflow_covers_trusted_and_validation_changes(workflow, event, path):
    trigger = workflow["on"][event]
    assert "branches" not in trigger and "branches-ignore" not in trigger
    assert any(fnmatchcase(path, pattern) for pattern in trigger["paths"])


def test_m1_workflow_keeps_all_required_validation_commands(workflow):
    steps = workflow["jobs"]["validate-m1-trusted-kernel"]["steps"]
    commands = {line.strip() for step in steps for line in step.get("run", "").splitlines()}
    assert {
        "bash scripts/run_m0_checks.sh", "python -m pytest", "git diff --check",
        "python scripts/run_m1_cli_smoke.py", "python scripts/verify_m1_frozen_baseline.py",
    } <= commands
    checkout = next(step for step in steps if step.get("uses", "").startswith("actions/checkout@"))
    assert checkout["with"]["fetch-depth"] == "0"
