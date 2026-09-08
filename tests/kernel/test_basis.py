"""Central system/basis validation and rejection of mixed S5 primitives."""

import pytest

from lewis_prover.errors import CertificateBasisError, NodeCheckError
from lewis_prover.kernel import (
    Ad, NodeChecker, PostulateInstance, ProofCertificate, ProofNode,
    certificate_from_document, instantiate_schema, load_frozen_spec, validate_basis,
)
from lewis_prover.syntax import And, Atom

P, Q = Atom("p"), Atom("q")
PRIMARY = "S5_PRIMARY_B1_B7_C11"
ALTERNATIVE = "S5_ALT_B1_B7_C10_C12"


@pytest.fixture(scope="module")
def frozen(repo_root):
    return load_frozen_spec(repo_root)


def node(frozen, schema_id):
    substitution = {"P": P}
    return ProofNode(instantiate_schema(schema_id, substitution, frozen), PostulateInstance(schema_id, substitution))


@pytest.mark.parametrize("system,basis_id", [
    ("S1", "S1_B1_B7"), ("S2", "S2_B1_B8"), ("S3", "S3_B1_B7_A8"),
    ("S4", "S4_B1_B7_C10"), ("S5", PRIMARY), ("S5", ALTERNATIVE),
])
def test_exact_basis_resolves_without_normalization(frozen, system, basis_id):
    assert validate_basis(system, basis_id, frozen) is frozen.bases[basis_id]


@pytest.mark.parametrize("system,basis_id", [
    ("S1", PRIMARY), ("S5", "S4_B1_B7_C10"), ("S6", PRIMARY),
    ("S5", "S5_UNION_B1_B7_C10_C11_C12"), ("s5", PRIMARY),
    ("S5 ", PRIMARY), ("S5", PRIMARY + " "), ("S5", "primary"),
    ("", PRIMARY), ("S5", ""), ("S5", [PRIMARY, ALTERNATIVE]), ([], PRIMARY),
])
def test_structural_loader_and_logical_checker_use_the_same_basis_rejection(frozen, system, basis_id):
    post = node(frozen, "B3")
    with pytest.raises(CertificateBasisError):
        validate_basis(system, basis_id, frozen)
    data = {
        "proof_id": "basis", "system": system, "basis_id": basis_id, "goal": post.conclusion.to_ast(),
        "root": "post", "nodes": {"post": {"conclusion": post.conclusion.to_ast(), "justification": {
            "kind": "postulate_instance", "schema_id": "B3", "schema_substitution": {"P": P.to_ast()},
        }}},
    }
    with pytest.raises(CertificateBasisError):
        certificate_from_document(data, frozen)
    cert = ProofCertificate("basis", system, basis_id, post.conclusion, "post", {"post": post})
    checker = NodeChecker(cert, frozen)
    with pytest.raises(NodeCheckError) as caught:
        checker.check_node("post")
    assert caught.value.code == "BASIS_IDENTITY" and checker.accepted_nodes == {}


@pytest.mark.parametrize("system,basis_id", [(1, PRIMARY), ("S5", None), ("S5", True), (None, PRIMARY)])
def test_no_numeric_or_null_basis_coercion(frozen, system, basis_id):
    with pytest.raises(CertificateBasisError):
        validate_basis(system, basis_id, frozen)


@pytest.mark.parametrize("basis_id,allowed,forbidden", [
    (PRIMARY, ("C11",), ("C10", "C12")),
    (ALTERNATIVE, ("C10", "C12"), ("C11",)),
])
def test_s5_primitive_union_is_rejected_even_inside_one_certificate(frozen, basis_id, allowed, forbidden):
    nodes = {schema_id: node(frozen, schema_id) for schema_id in ("C10", "C11", "C12")}
    nodes["mixed"] = ProofNode(And(nodes["C11"].conclusion, nodes["C10"].conclusion), Ad(("C11", "C10")))
    cert = ProofCertificate("mixed-basis", "S5", basis_id, nodes["mixed"].conclusion, "mixed", nodes)
    checker = NodeChecker(cert, frozen)
    for schema_id in allowed:
        checker.check_node(schema_id)
    for schema_id in forbidden:
        with pytest.raises(NodeCheckError) as caught:
            checker.check_node(schema_id)
        assert caught.value.code == "SCHEMA_ADMISSION"
        assert schema_id not in checker.accepted_nodes
    with pytest.raises(NodeCheckError) as caught:
        checker.check_node("mixed")
    assert caught.value.code == "PARENT_NOT_ACCEPTED"


def test_no_inherited_primitive_union_or_cross_session_parent_import(frozen):
    primary = validate_basis("S5", PRIMARY, frozen)
    alternative = validate_basis("S5", ALTERNATIVE, frozen)
    assert "C11" in primary.schemas and not {"C10", "C12"} & primary.schemas
    assert {"C10", "C12"} <= alternative.schemas and "C11" not in alternative.schemas
    first_node, second_node = node(frozen, "C11"), node(frozen, "C10")
    nodes = {"first": first_node, "second": second_node,
             "ad": ProofNode(And(first_node.conclusion, second_node.conclusion), Ad(("first", "second")))}
    first = NodeChecker(ProofCertificate("p", "S5", PRIMARY, P, "ad", nodes), frozen)
    second = NodeChecker(ProofCertificate("a", "S5", ALTERNATIVE, P, "ad", nodes), frozen)
    first.check_node("first")
    second.check_node("second")
    for checker in (first, second):
        with pytest.raises(NodeCheckError) as caught:
            checker.check_node("ad")
        assert caught.value.code == "PARENT_NOT_ACCEPTED"
