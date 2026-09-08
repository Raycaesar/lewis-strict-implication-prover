"""Verifier CLI smoke tests, including subprocess entry point and exit codes."""

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest
import yaml

from lewis_prover import cli
from lewis_prover.errors import CertificateValidationError
from lewis_prover.kernel import check_certificate

KINDS = ("postulate_instance", "Sa", "Sb", "Ad", "Smp", "definition_conversion")


def run_cli(repo_root, *args, cwd=None):
    return subprocess.run(
        [sys.executable, "-m", "lewis_prover", *map(str, args)],
        cwd=repo_root if cwd is None else cwd,
        env={**os.environ, "PYTHONPATH": str(repo_root / "src")},
        capture_output=True, text=True, encoding="utf-8", timeout=30,
    )


def result(process, status, exit_code):
    assert process.returncode == exit_code, process.stderr
    assert process.stderr == ""
    lines = process.stdout.splitlines()
    assert len(lines) == 2 and lines[0] == status
    return json.loads(lines[1])


@pytest.mark.parametrize("kind", KINDS)
def test_each_positive_fixture_through_module_cli(repo_root, m1_fixture_dir, kind):
    path = m1_fixture_dir / f"{kind}.json"
    data = json.loads(path.read_bytes())
    first = run_cli(repo_root, "verify", path)
    detail = result(first, "VALID_CERTIFICATE", 0)
    assert detail == {
        "proof_id": data["proof_id"], "system": data["system"], "basis_id": data["basis_id"],
        "root": data["root"], "node_count": len(data["nodes"]),
    }
    assert run_cli(repo_root, "verify", path).stdout == first.stdout


def test_explicit_spec_root_from_another_working_directory(repo_root, m1_fixture_dir, tmp_path):
    process = run_cli(repo_root, "verify", m1_fixture_dir / "Ad.json", "--spec-root", repo_root, cwd=tmp_path)
    result(process, "VALID_CERTIFICATE", 0)
    # No implicit search back to the source repository if cwd has no basis.
    process = run_cli(repo_root, "verify", m1_fixture_dir / "Ad.json", cwd=tmp_path)
    assert result(process, "INVALID_CERTIFICATE", 2)["code"] == "frozen_spec_error"


@pytest.mark.parametrize("payload,code", [
    (b'{"root":"a","root":"b"}', "document_decode_error"),
    (b'\xff', "document_decode_error"), (b'\xef\xbb\xbf{}', "document_decode_error"),
    (b'{"x":"\\ud800"}', "document_decode_error"),
    (b'{"x":NaN}', "document_decode_error"), (b'{"x":null}', "document_decode_error"),
    (b'{}', "closed_world_field_error"),
])
def test_invalid_bytes_and_structure_return_nonzero(repo_root, tmp_path, payload, code):
    path = tmp_path / "invalid.json"
    path.write_bytes(payload)
    assert result(run_cli(repo_root, "verify", path), "INVALID_CERTIFICATE", 1)["code"] == code


@pytest.mark.parametrize("kind", KINDS)
def test_cli_preserves_structured_logical_error(repo_root, m1_frozen, m1_document, tmp_path, kind):
    data = m1_document(kind)
    data["nodes"]["root"]["conclusion"] = {"op": "atom", "name": "wrong"}
    payload = json.dumps(data).encode()
    with pytest.raises(CertificateValidationError) as caught:
        check_certificate(payload, m1_frozen)
    path = tmp_path / "logical-error.json"
    path.write_bytes(payload)
    detail = result(run_cli(repo_root, "verify", path), "INVALID_CERTIFICATE", 1)
    error = caught.value
    assert detail == {"code": "invalid_" + kind, "detail_code": error.detail_code, "kind": kind,
                      "node_id": "root", "reason": error.reason, "related_ids": []}


@pytest.mark.parametrize("mutation,detail_code", [
    ("status", "FrozenSpecStatusError"), ("contract", "FrozenContractError"),
    ("ast", "FrozenSpecFingerprintError"), ("duplicate", "FrozenSpecFormatError"),
])
def test_cli_refuses_altered_or_nonfrozen_spec(repo_root, copied_candidate, m1_fixture_dir, mutation, detail_code):
    path = copied_candidate / "spec" / "rules.yaml"
    original = path.read_text(encoding="utf-8")
    data = yaml.safe_load(original)
    if mutation == "status":
        data["status"] = "candidate_m0"
    elif mutation == "contract":
        data["canonical_certificate_contract"]["kinds"]["Sb"]["replacement_count"] = 2
    elif mutation == "ast":
        path = copied_candidate / "spec" / "schemas.yaml"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        data["schemas"]["B3"]["ast"] = {"meta": "P"}
    if mutation == "duplicate":
        path.write_text(original + "\nstatus: frozen_m0\n", encoding="utf-8")
    else:
        path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")
    process = run_cli(repo_root, "verify", m1_fixture_dir / "postulate_instance.json", "--spec-root", copied_candidate)
    detail = result(process, "INVALID_CERTIFICATE", 2)
    assert detail["code"] == "frozen_spec_error" and detail["detail_code"] == detail_code


@pytest.mark.parametrize("args", [[], ["prove", "p"], ["verify"], ["verify", "x.json", "--allow-unfrozen"],
                                  ["verify", "x.json", "--spec-r", "."]])
def test_no_prove_command_missing_arguments_or_hidden_overrides(repo_root, args):
    assert result(run_cli(repo_root, *args), "INVALID_CERTIFICATE", 2)["code"] == "usage_error"


@pytest.mark.parametrize("args", [["--help"], ["verify", "--help"]])
def test_help_cannot_be_mistaken_for_successful_verification(repo_root, args):
    detail = result(run_cli(repo_root, *args), "INVALID_CERTIFICATE", 2)
    assert detail["code"] == "help_requested"
    assert "verify" in detail["help"]


@pytest.mark.parametrize("target", ["missing.json", "."])
def test_unreadable_certificate_has_no_success_exit(repo_root, tmp_path, target):
    process = run_cli(repo_root, "verify", tmp_path / target)
    assert result(process, "INVALID_CERTIFICATE", 2)["code"] == "certificate_io_error"


def test_spec_is_authenticated_before_reading_certificate(m1_fixture_dir, monkeypatch, capsys):
    from lewis_prover.errors import FrozenSpecStatusError

    def rejected(root):
        raise FrozenSpecStatusError("not frozen")

    def must_not_read(path):
        pytest.fail("certificate was read before authenticating the frozen basis")

    monkeypatch.setattr(cli, "load_frozen_spec", rejected)
    monkeypatch.setattr(Path, "read_bytes", must_not_read)
    assert cli.main(["verify", str(m1_fixture_dir / "Sa.json")]) == 2
    assert capsys.readouterr().out.splitlines()[0] == "INVALID_CERTIFICATE"


def test_unexpected_frontend_failure_fails_closed(m1_fixture_dir, monkeypatch, capsys):
    def broken(root):
        raise RuntimeError("test-only internal failure")

    monkeypatch.setattr(cli, "load_frozen_spec", broken)
    assert cli.main(["verify", str(m1_fixture_dir / "Sa.json")]) == 2
    lines = capsys.readouterr().out.splitlines()
    assert lines[0] == "INVALID_CERTIFICATE"
    assert json.loads(lines[1])["code"] == "internal_error"
