"""Regressions for Work Max's unchecked formula-declaration P0.

Only temporary copies are mutated. No weakened FrozenSpec is constructed and
no production integrity check is bypassed to make a negative test pass.
"""

import json
import shutil
from pathlib import Path

import pytest
import yaml

from lewis_prover import cli
from lewis_prover.errors import (
    CertificateValidationError, FrozenContractError, FrozenSpecFingerprintError,
    FrozenSpecIntegrityError, SchemaMatchError,
)
from lewis_prover.kernel import (
    check_certificate, convert_definition, instantiate_schema, load_frozen_spec,
    match_schema, object_atom_names, replace_occurrence, resolve_occurrence,
    schema_metavariables, substitute_atoms,
)
from lewis_prover.kernel import frozen_spec as loader
from lewis_prover.kernel.frozen_baseline import FROZEN_INPUT_SHA256
from lewis_prover.syntax import (
    And, Atom, EquivS, Neg, Or, Poss, StrictImp, diagnostic_full_erasure,
)

INPUTS = (
    "spec/language.yaml", "spec/rules.yaml", "spec/schemas.yaml", "spec/systems.yaml",
    "audit/m0/certified_ast_fingerprints.yaml", "audit/m0/certificate_contract_lock.yaml",
)
OPS = ("atom", "neg", "poss", "and", "or", "strict_imp", "equiv_s")
DEFINED = ("or", "strict_imp", "equiv_s")
KINDS = ("postulate_instance", "Sa", "Sb", "Ad", "Smp", "definition_conversion")


@pytest.fixture
def baseline_copy(tmp_path, repo_root):
    for relative in INPUTS:
        target = tmp_path / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(repo_root / relative, target)
    return tmp_path


def mutate(root, relative, change):
    path = root / relative
    value = yaml.safe_load(path.read_bytes())
    change(value)
    path.write_text(yaml.safe_dump(value, sort_keys=False, allow_unicode=True), encoding="utf-8")


def skip_right_child(value):
    value["formula_ast"]["and"]["fields"] = ["left"]


@pytest.fixture
def forbid_trusted_construction(monkeypatch):
    def reached(*args, **kwargs):
        pytest.fail("trusted structures were constructed before baseline integrity passed")

    monkeypatch.setattr(loader, "FrozenBasis", reached)
    monkeypatch.setattr(loader, "FrozenSpec", reached)
    monkeypatch.setattr(loader, "deep_freeze", reached)


def test_manifest_covers_exactly_all_production_inputs():
    assert set(FROZEN_INPUT_SHA256) == set(INPUTS)


@pytest.mark.parametrize("kind", KINDS)
def test_ordinary_copied_baseline_accepts_all_six_kinds(baseline_copy, repo_root, kind):
    # No .git, audit/m1, or copy of the checker manifest is required here.
    frozen = load_frozen_spec(baseline_copy)
    payload = (repo_root / "tests/fixtures/m1" / f"{kind}.json").read_bytes()
    checked = check_certificate(payload, frozen)
    assert checked.certificate.nodes[checked.certificate.root].justification.kind == kind


@pytest.mark.parametrize("relative", INPUTS)
def test_complete_file_identity_includes_bytes_outside_old_locks(
    baseline_copy, relative, forbid_trusted_construction,
):
    path = baseline_copy / relative
    # Parsed-object equality and every old semantic validation still pass.
    path.write_bytes(path.read_bytes() + b"\n# temporary integrity regression\n")
    with pytest.raises(FrozenSpecIntegrityError, match=relative):
        load_frozen_spec(baseline_copy)


@pytest.mark.parametrize("op", OPS)
@pytest.mark.parametrize("change", (
    "fields", "renamed_fields", "missing_fields", "arity", "primitive",
    "object_level", "missing_constructor",
))
def test_every_constructor_declaration_mutation_rejects_before_trusted_construction(
    baseline_copy, op, change, forbid_trusted_construction,
):
    def alter(value):
        registry = value["formula_ast"]
        declaration = registry[op]
        if change == "fields":
            declaration["fields"] = []
        elif change == "renamed_fields":
            declaration["fields"] = ["unregistered_child"]
        elif change == "missing_fields":
            del declaration["fields"]
        elif change == "arity":
            declaration["arity"] += 1
        elif change in ("primitive", "object_level"):
            declaration[change] = not declaration[change]
        else:
            del registry[op]

    mutate(baseline_copy, "spec/language.yaml", alter)
    with pytest.raises(FrozenSpecIntegrityError, match="spec/language.yaml"):
        load_frozen_spec(baseline_copy)


@pytest.mark.parametrize("op", ("and", "or", "strict_imp", "equiv_s"))
def test_constructor_child_order_is_frozen(baseline_copy, op, forbid_trusted_construction):
    mutate(baseline_copy, "spec/language.yaml", lambda value: value["formula_ast"][op]["fields"].reverse())
    with pytest.raises(FrozenSpecIntegrityError):
        load_frozen_spec(baseline_copy)


@pytest.mark.parametrize("op", DEFINED)
@pytest.mark.parametrize("field,value", (
    ("definition_id", "DEF_UNREGISTERED"), ("definition_id", None),
    ("definition_id", "another_registered_definition"),
    ("first_class_surface_node", False),
))
def test_defined_constructor_link_and_classification_are_frozen(
    baseline_copy, op, field, value, forbid_trusted_construction,
):
    def alter(document):
        declaration = document["formula_ast"][op]
        if value is None:
            del declaration[field]
        elif value == "another_registered_definition":
            declaration[field] = "DEF_OR" if op != "or" else "DEF_EQUIV_S"
        else:
            declaration[field] = value

    mutate(baseline_copy, "spec/language.yaml", alter)
    with pytest.raises(FrozenSpecIntegrityError):
        load_frozen_spec(baseline_copy)


@pytest.mark.parametrize("definition_id", ("DEF_OR", "DEF_STRICT_IMP", "DEF_EQUIV_S"))
def test_conversion_registry_lhs_association_keeps_ast_lock_defense(
    baseline_copy, definition_id, forbid_trusted_construction,
):
    mutate(baseline_copy, "spec/language.yaml", lambda value:
           value["metadefinitions"][definition_id]["lhs"].__setitem__("op", "and"))
    with pytest.raises(FrozenSpecFingerprintError, match=definition_id):
        load_frozen_spec(baseline_copy)


def invalid_conversion(repo_root, downstream):
    data = json.loads((repo_root / "tests/fixtures/m1/invalid/definition_conversion_skipped_reverse.json").read_bytes())
    if downstream == "definition_conversion":
        return data
    equivalence = data["nodes"].pop("root")
    data["nodes"]["equivalence"] = equivalence
    p = Atom("p")
    claim = EquivS(p, Neg(Neg(p)))
    forward = StrictImp(p, Neg(Neg(p)))
    if downstream == "Sb":
        conclusion = StrictImp(Neg(Neg(p)), Neg(Neg(p)))
        justification = {"kind": "Sb", "parents": ["equivalence", "forward"],
                         "direction": "left_to_right", "occurrence_path": ["left"]}
    elif downstream == "Sa":
        q = Atom("q")
        conclusion = EquivS(q, Neg(Neg(q)))
        justification = {"kind": "Sa", "parents": ["equivalence"], "atom_substitution": {"p": q.to_ast()}}
    elif downstream == "Ad":
        conclusion = And(claim, forward)
        justification = {"kind": "Ad", "parents": ["equivalence", "forward"]}
    else:
        assert downstream == "Smp"
        conclusion = Neg(Neg(claim))
        data["nodes"]["implication"] = {
            "conclusion": StrictImp(claim, conclusion).to_ast(),
            "justification": {"kind": "postulate_instance", "schema_id": "B5",
                              "schema_substitution": {"P": claim.to_ast()}},
        }
        justification = {"kind": "Smp", "parents": ["equivalence", "implication"]}
    data["goal"] = conclusion.to_ast()
    data["nodes"]["root"] = {"conclusion": conclusion.to_ast(), "justification": justification}
    return data


@pytest.mark.parametrize("downstream", ("definition_conversion", "Sb", "Sa", "Ad", "Smp"))
def test_skipped_reverse_implication_and_its_downstream_uses_reject(
    baseline_copy, repo_root, downstream,
):
    payload = json.dumps(invalid_conversion(repo_root, downstream))
    # Establish the exact invalid derivation, not a graph/structure failure.
    with pytest.raises(CertificateValidationError) as caught:
        check_certificate(payload, load_frozen_spec(baseline_copy))
    assert caught.value.code == "invalid_definition_conversion"
    assert caught.value.detail_code == "DEFINITION_CONVERSION"
    assert caught.value.node_id == ("root" if downstream == "definition_conversion" else "equivalence")

    # On d87f114, this mutation let the invalid conversion reach acceptance.
    mutate(baseline_copy, "spec/language.yaml", skip_right_child)
    with pytest.raises(FrozenSpecIntegrityError, match="spec/language.yaml"):
        check_certificate(payload, load_frozen_spec(baseline_copy))


def test_schema_match_cannot_skip_repeated_metavariable(baseline_copy):
    invalid = StrictImp(And(Atom("p"), Atom("q")), And(Atom("q"), Atom("r")))
    with pytest.raises(SchemaMatchError, match="inconsistent repeated"):
        match_schema("B1", invalid, load_frozen_spec(baseline_copy))
    mutate(baseline_copy, "spec/language.yaml", skip_right_child)
    with pytest.raises(FrozenSpecIntegrityError):
        match_schema("B1", invalid, load_frozen_spec(baseline_copy))


def exercise_transform(operation, frozen):
    p, q, r = Atom("p"), Atom("q"), Atom("r")
    source = And(p, Or(q, r))
    if operation == "schema_instantiation":
        assert instantiate_schema("B1", {"P": p, "Q": q}, frozen) == StrictImp(And(p, q), And(q, p))
    elif operation == "schema_metavariables":
        assert schema_metavariables("B1", frozen) == {"P", "Q"}
    elif operation == "occurrence_resolution":
        assert resolve_occurrence(source, ["right", "left"], frozen) == q
    elif operation == "occurrence_replacement":
        assert replace_occurrence(source, ["right", "left"], p, frozen) == And(p, Or(p, r))
    elif operation == "atom_names":
        assert object_atom_names(source, frozen) == {"p", "q", "r"}
    elif operation == "Sa":
        assert substitute_atoms(source, {"q": p}, frozen) == And(p, Or(p, r))
    elif operation == "definition_expansion":
        assert convert_definition(Or(p, q), "DEF_OR", "expand", [], frozen) == Neg(And(Neg(p), Neg(q)))
    else:
        assert operation == "diagnostic_erasure"
        assert diagnostic_full_erasure(StrictImp(p, q), frozen) == Neg(Poss(And(p, Neg(q))))


@pytest.mark.parametrize("operation", (
    "schema_instantiation", "schema_metavariables", "occurrence_resolution",
    "occurrence_replacement", "atom_names", "Sa", "definition_expansion", "diagnostic_erasure",
))
def test_all_spec_using_transform_paths_require_an_intact_baseline(baseline_copy, operation):
    exercise_transform(operation, load_frozen_spec(baseline_copy))
    mutate(baseline_copy, "spec/language.yaml", skip_right_child)
    with pytest.raises(FrozenSpecIntegrityError):
        exercise_transform(operation, load_frozen_spec(baseline_copy))


@pytest.mark.parametrize("op", OPS)
def test_occurrence_and_sb_traversal_declarations_keep_contract_lock_defense(
    baseline_copy, op, forbid_trusted_construction,
):
    mutate(baseline_copy, "spec/rules.yaml", lambda value:
           value["canonical_certificate_contract"]["occurrence_path"]["traversable_fields"].__setitem__(op, ["name"]))
    with pytest.raises(FrozenContractError, match="contract fingerprint mismatch"):
        load_frozen_spec(baseline_copy)


@pytest.mark.parametrize("change", ("legal_segments", "root_replacement_allowed"))
def test_occurrence_and_sb_policy_keep_contract_lock_defense(baseline_copy, change):
    def alter(value):
        contract = value["canonical_certificate_contract"]
        if change == "legal_segments":
            contract["occurrence_path"]["legal_segments"].append("name")
        else:
            contract["kinds"]["Sb"]["root_replacement_allowed"] = False

    mutate(baseline_copy, "spec/rules.yaml", alter)
    with pytest.raises(FrozenContractError):
        load_frozen_spec(baseline_copy)


def test_cli_p0_rejects_before_certificate_read_or_theorem_check(
    baseline_copy, repo_root, monkeypatch, capsys,
):
    path = repo_root / "tests/fixtures/m1/invalid/definition_conversion_skipped_reverse.json"
    mutate(baseline_copy, "spec/language.yaml", skip_right_child)
    original_read = Path.read_bytes

    def guarded_read(candidate):
        assert candidate != path, "certificate read before rejecting corrupt baseline"
        return original_read(candidate)

    def forbidden_check(*args):
        pytest.fail("theorem checking began with corrupted constructor declarations")

    monkeypatch.setattr(Path, "read_bytes", guarded_read)
    monkeypatch.setattr(cli, "check_certificate", forbidden_check)
    assert cli.main(["verify", str(path), "--spec-root", str(baseline_copy)]) == 2
    lines = capsys.readouterr().out.splitlines()
    assert lines[0] == "INVALID_CERTIFICATE"
    detail = json.loads(lines[1])
    assert (detail["code"], detail["detail_code"]) == ("frozen_spec_error", "FrozenSpecIntegrityError")


@pytest.mark.parametrize("initially_valid", (True, False))
def test_validation_and_parsing_use_the_same_single_read_snapshot(
    baseline_copy, monkeypatch, initially_valid,
):
    target = baseline_copy / "spec/language.yaml"
    original = target.read_bytes()
    mutate(baseline_copy, "spec/language.yaml", skip_right_child)
    corrupted = target.read_bytes()
    target.write_bytes(original if initially_valid else corrupted)
    original_read = Path.read_bytes
    reads = []

    def change_after_read(path):
        data = original_read(path)
        reads.append(path.relative_to(baseline_copy).as_posix())
        if path == target:
            path.write_bytes(corrupted if initially_valid else original)
        return data

    with monkeypatch.context() as scoped:
        scoped.setattr(Path, "read_bytes", change_after_read)
        if initially_valid:
            frozen = load_frozen_spec(baseline_copy)
            exercise_transform("schema_instantiation", frozen)
        else:
            with pytest.raises(FrozenSpecIntegrityError):
                load_frozen_spec(baseline_copy)
    assert sorted(reads) == sorted(INPUTS)
    # Later filesystem changes cannot change the previously frozen result.
    if initially_valid:
        exercise_transform("definition_expansion", frozen)
        with pytest.raises(FrozenSpecIntegrityError):
            load_frozen_spec(baseline_copy)


def test_caller_supplied_manifest_cannot_authorize_a_changed_spec(baseline_copy):
    mutate(baseline_copy, "spec/language.yaml", skip_right_child)
    fake = baseline_copy / "src/lewis_prover/kernel/frozen_baseline.py"
    fake.parent.mkdir(parents=True)
    fake.write_text("FROZEN_INPUT_SHA256 = {}\n")
    with pytest.raises(FrozenSpecIntegrityError):
        load_frozen_spec(baseline_copy)
