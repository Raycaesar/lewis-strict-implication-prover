"""Closed structural values: these tests intentionally do not prove theorems."""

import copy
import json
from dataclasses import FrozenInstanceError

import pytest

from lewis_prover.errors import (
    CertificateDocumentError, CertificateFieldError, CertificateIdentifierError,
    CertificateStructureError, CertificateValueTypeError, DuplicateCertificateKeyError,
)
from lewis_prover.kernel import (
    Ad, DefinitionConversion, PostulateInstance, ProofCertificate, ProofNode,
    Sa, Sb, Smp, certificate_from_document, decode_certificate_document,
    load_certificate, load_frozen_spec,
)
from lewis_prover.syntax import Atom, StrictImp

ATOM = {"op": "atom", "name": "p"}
JUSTIFICATIONS = [
    {"kind": "postulate_instance", "schema_id": "B1", "schema_substitution": {"P": ATOM, "Q": ATOM}},
    {"kind": "Sa", "parents": ["n1"], "atom_substitution": {"p": ATOM}},
    {"kind": "Sb", "parents": ["n1", "n2"], "direction": "left_to_right", "occurrence_path": []},
    {"kind": "Ad", "parents": ["n1", "n2"]},
    {"kind": "Smp", "parents": ["n1", "n2"]},
    {"kind": "definition_conversion", "parents": ["n1"], "definition_id": "DEF_OR",
     "direction": "expand", "occurrence_path": ["arg", "left"]},
]
MODELS = [PostulateInstance, Sa, Sb, Ad, Smp, DefinitionConversion]


@pytest.fixture(scope="module")
def frozen(repo_root):
    return load_frozen_spec(repo_root)


def proof(kind=0):
    return copy.deepcopy({
        "proof_id": "proof", "system": "S1", "basis_id": "S1_B1_B7",
        "goal": ATOM, "root": "n1",
        "nodes": {"n1": {"conclusion": ATOM, "justification": JUSTIFICATIONS[kind]}},
    })


@pytest.mark.parametrize("kind", range(6))
@pytest.mark.parametrize("as_bytes", [False, True])
def test_all_six_minimal_structural_certificates(frozen, kind, as_bytes):
    source = json.dumps(proof(kind))
    loaded = load_certificate(source.encode() if as_bytes else source, frozen)
    assert isinstance(loaded, ProofCertificate)
    assert isinstance(loaded.nodes["n1"], ProofNode)
    assert type(loaded.nodes["n1"].justification) is MODELS[kind]
    assert loaded.nodes["n1"].justification.kind == JUSTIFICATIONS[kind]["kind"]
    assert loaded.goal == Atom("p")
    assert loaded == certificate_from_document(decode_certificate_document(source), frozen)


@pytest.mark.parametrize("kind", range(6))
def test_missing_and_unknown_fields_at_every_closed_level(frozen, kind):
    def targets(value):
        node = value["nodes"]["n1"]
        return [value, node, node["justification"]]

    for level in range(3):
        original_fields = list(targets(proof(kind))[level])
        for field in original_fields:
            data = proof(kind)
            del targets(data)[level][field]
            with pytest.raises(CertificateStructureError):
                load_certificate(json.dumps(data), frozen)
        for extra in ("metadata", "extra", "line_number", "parent"):
            data = proof(kind)
            targets(data)[level][extra] = "forbidden"
            with pytest.raises(CertificateFieldError, match="unknown fields"):
                load_certificate(json.dumps(data), frozen)


@pytest.mark.parametrize("location", ["goal", "conclusion", "schema_substitution", "atom_substitution"])
@pytest.mark.parametrize("bad_formula", [
    {"op": "atom", "name": "p", "extra": "x"},
    {"op": "neg", "arg": {"op": "atom", "name": "p", "extra": "x"}},
    {"meta": "P"}, {"op": []}, {"op": "neg", "arg": {"op": {}}},
    {"op": "atom", "name": ""}, {"op": "box", "arg": ATOM},
    {"op": "strict_imp", "left": ATOM}, [], "p",
])
def test_formula_fields_are_closed_at_all_locations(frozen, location, bad_formula):
    data = proof(1 if location == "atom_substitution" else 0)
    node = data["nodes"]["n1"]
    if location == "goal":
        data["goal"] = bad_formula
    elif location == "conclusion":
        node["conclusion"] = bad_formula
    else:
        node["justification"][location]["P"] = bad_formula
    with pytest.raises(CertificateStructureError):
        load_certificate(json.dumps(data), frozen)


@pytest.mark.parametrize("kind", range(1, 6))
@pytest.mark.parametrize("parents", [[], ["n1"] * 3, "n1", {}, [""]])
def test_parent_arrays_counts_and_nonempty_references(frozen, kind, parents):
    data = proof(kind)
    data["nodes"]["n1"]["justification"]["parents"] = parents
    with pytest.raises(CertificateStructureError):
        load_certificate(json.dumps(data), frozen)


@pytest.mark.parametrize("kind", [2, 5])
@pytest.mark.parametrize("field,value", [
    ("direction", "invalid"), ("direction", []), ("occurrence_path", "arg"),
    ("occurrence_path", ["name"]), ("occurrence_path", [""]),
    ("occurrence_path", [[]]), ("occurrence_path", {}),
])
def test_directions_and_occurrence_path_shape(frozen, kind, field, value):
    data = proof(kind)
    data["nodes"]["n1"]["justification"][field] = value
    with pytest.raises(CertificateStructureError):
        load_certificate(json.dumps(data), frozen)


@pytest.mark.parametrize("kind,direction", [(2, "right_to_left"), (5, "contract")])
def test_other_allowed_directions_and_empty_root_paths(frozen, kind, direction):
    data = proof(kind)
    data["nodes"]["n1"]["justification"].update(direction=direction, occurrence_path=[])
    assert load_certificate(json.dumps(data), frozen).nodes["n1"].justification.direction == direction


@pytest.mark.parametrize("kind", [[], {}, "", "axiom", "theorem_library_lookup", "Box"])
def test_unknown_kind(frozen, kind):
    data = proof()
    data["nodes"]["n1"]["justification"]["kind"] = kind
    with pytest.raises(CertificateStructureError):
        load_certificate(json.dumps(data), frozen)


@pytest.mark.parametrize("location", ["proof_id", "root", "parent", "schema_id", "definition_id"])
@pytest.mark.parametrize("value", ["", [], {}])
def test_identifier_policy(frozen, location, value):
    data = proof(5 if location == "definition_id" else 1 if location == "parent" else 0)
    if location in ("proof_id", "root"):
        data[location] = value
    elif location == "parent":
        data["nodes"]["n1"]["justification"]["parents"] = [value]
    else:
        data["nodes"]["n1"]["justification"][location] = value
    with pytest.raises(CertificateIdentifierError):
        load_certificate(json.dumps(data), frozen)


def test_empty_node_id(frozen):
    data = proof()
    data["nodes"][""] = data["nodes"].pop("n1")
    with pytest.raises(CertificateIdentifierError):
        load_certificate(json.dumps(data), frozen)


@pytest.mark.parametrize("kind", [0, 1])
@pytest.mark.parametrize("value", [[], "wrong", {"": ATOM}])
def test_substitution_object_and_key_types(frozen, kind, value):
    data = proof(kind)
    field = "schema_substitution" if kind == 0 else "atom_substitution"
    data["nodes"]["n1"]["justification"][field] = value
    with pytest.raises(CertificateStructureError):
        load_certificate(json.dumps(data), frozen)


def test_sa_substitution_must_be_nonempty(frozen):
    data = proof(1)
    data["nodes"]["n1"]["justification"]["atom_substitution"] = {}
    with pytest.raises(CertificateStructureError, match="nonempty"):
        load_certificate(json.dumps(data), frozen)


@pytest.mark.parametrize("location", ["proof_id", "root", "parent", "schema_id", "definition_id"])
@pytest.mark.parametrize("number", [0, 1, 1.0, True, None])
def test_numeric_reference_coercion_rejected_by_document_stage(frozen, location, number):
    data = proof(5 if location == "definition_id" else 1 if location == "parent" else 0)
    if location in ("proof_id", "root"):
        data[location] = number
    elif location == "parent":
        data["nodes"]["n1"]["justification"]["parents"] = [number]
    else:
        data["nodes"]["n1"]["justification"][location] = number
    with pytest.raises(CertificateValueTypeError):
        load_certificate(json.dumps(data), frozen)


def test_unquoted_numeric_node_keys_and_in_memory_numeric_keys(frozen):
    with pytest.raises(CertificateDocumentError):
        load_certificate('{"nodes":{1:{}}}', frozen)
    data = proof()
    data["nodes"][1] = data["nodes"].pop("n1")
    with pytest.raises(CertificateValueTypeError):
        certificate_from_document(data, frozen)


def test_exact_reference_identity_without_trimming_normalization_or_coercion(frozen):
    data = proof(3)
    node = data["nodes"].pop("n1")
    names = ["1", "01", " 1 ", "é", "e\u0301", " "]
    data.update(proof_id=" ", root="01", nodes={name: copy.deepcopy(node) for name in names})
    data["nodes"]["01"]["justification"]["parents"] = ["é", "e\u0301"]
    cert = load_certificate(json.dumps(data), frozen)
    assert cert.proof_id == " " and cert.root == "01"
    assert list(cert.nodes) == names
    assert cert.nodes["01"].justification.parents == ("é", "e\u0301")


def test_document_validation_completes_before_structural_loading(frozen, monkeypatch):
    from lewis_prover.kernel import certificate as production

    def should_not_run(*args):
        pytest.fail("structural loading started for an invalid serialized document")
    monkeypatch.setattr(production, "certificate_from_document", should_not_run)
    with pytest.raises(DuplicateCertificateKeyError):
        production.load_certificate('{"unknown":"field","nested":{"x":"a","x":"b"}}', frozen)
    with pytest.raises(CertificateValueTypeError):
        production.load_certificate('{"unknown":"field","nested":{"x":1}}', frozen)


def test_structure_is_not_a_logical_validity_check(frozen):
    data = proof(4)  # Smp with an atom conclusion and no implication premise
    data["goal"] = {"op": "strict_imp", "left": ATOM, "right": ATOM}
    data["nodes"]["n1"]["justification"]["parents"] = ["n1", "missing"]
    data["root"] = "unresolved"
    cert = load_certificate(json.dumps(data), frozen)
    assert cert.nodes["n1"].justification.parents == ("n1", "missing")
    assert cert.root == "unresolved"
    assert cert.goal == StrictImp(Atom("p"), Atom("p"))
    assert cert.goal != cert.nodes["n1"].conclusion


@pytest.mark.parametrize("system,basis_id", [
    ("S1", "S5_PRIMARY_B1_B7_C11"), ("S5", "S5_UNION"), ("S6", "S1_B1_B7"),
])
def test_frozen_system_basis_identity(frozen, system, basis_id):
    data = proof()
    data.update(system=system, basis_id=basis_id)
    with pytest.raises(CertificateStructureError):
        load_certificate(json.dumps(data), frozen)


@pytest.mark.parametrize("basis", ["S5_PRIMARY_B1_B7_C11", "S5_ALT_B1_B7_C10_C12"])
def test_s5_bases_stay_separate(frozen, basis):
    data = proof()
    data.update(system="S5", basis_id=basis)
    assert load_certificate(json.dumps(data), frozen).basis_id == basis


@pytest.mark.parametrize("kind", range(6))
def test_immutable_models_and_detached_input(frozen, kind):
    data = proof(kind)
    cert = certificate_from_document(data, frozen)
    node = cert.nodes["n1"]
    justification = node.justification
    with pytest.raises(FrozenInstanceError):
        cert.root = "changed"
    with pytest.raises(TypeError):
        cert.nodes["new"] = node
    with pytest.raises(FrozenInstanceError):
        node.conclusion = Atom("changed")
    with pytest.raises((FrozenInstanceError, TypeError, AttributeError)):
        justification.kind = "Ad"
    if kind in (0, 1):
        field = "schema_substitution" if kind == 0 else "atom_substitution"
        substitution = getattr(justification, field)
        key = next(iter(substitution))
        with pytest.raises(TypeError):
            substitution[key] = Atom("changed")
        data["nodes"]["n1"]["justification"][field][key]["name"] = "changed"
        assert substitution[key] == Atom("p")
    if kind:
        with pytest.raises(TypeError):
            justification.parents[0] = "changed"
        data["nodes"]["n1"]["justification"]["parents"][0] = "changed"
        assert justification.parents[0] == "n1"
    if kind in (2, 5):
        assert isinstance(justification.occurrence_path, tuple)
        data["nodes"]["n1"]["justification"]["occurrence_path"].append("right")
        assert justification.occurrence_path == tuple(JUSTIFICATIONS[kind]["occurrence_path"])
    data["goal"]["name"] = "changed"
    data["nodes"].clear()
    assert cert.goal == Atom("p")
    assert "n1" in cert.nodes


def test_direct_model_builders_copy_mutable_containers():
    substitution = {"P": Atom("p")}
    post = PostulateInstance("B1", substitution)
    parents = ["n1", "n2"]
    path = ["arg"]
    sb = Sb(parents, "left_to_right", path)
    node = ProofNode(Atom("p"), post)
    nodes = {"n1": node}
    cert = ProofCertificate("p", "S1", "S1_B1_B7", Atom("p"), "n1", nodes)
    substitution.clear()
    parents.clear()
    path.clear()
    nodes.clear()
    assert post.schema_substitution == {"P": Atom("p")}
    assert sb.parents == ("n1", "n2") and sb.occurrence_path == ("arg",)
    assert cert.nodes == {"n1": node}
