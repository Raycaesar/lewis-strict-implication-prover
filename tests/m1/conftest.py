"""Fixtures for implementation-level M1 hardening, independent of M0 validators."""

import json

import pytest

from lewis_prover.kernel import load_frozen_spec


@pytest.fixture(scope="session")
def m1_frozen(repo_root):
    return load_frozen_spec(repo_root)


@pytest.fixture(scope="session")
def m1_fixture_dir(repo_root):
    return repo_root / "tests" / "fixtures" / "m1"


@pytest.fixture
def m1_document(m1_fixture_dir):
    def load(kind):
        return json.loads((m1_fixture_dir / f"{kind}.json").read_bytes())
    return load
