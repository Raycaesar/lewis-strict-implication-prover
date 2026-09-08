"""Acceptance and rejection for the first three logical node checks."""

import json
from dataclasses import dataclass, replace
from types import SimpleNamespace

import pytest

from lewis_prover.errors import CertificateFieldError, NodeCheckError
from lewis_prover.kernel import (
    Ad, DefinitionConversion, NodeChecker, PostulateInstance, ProofCertificate,
    ProofNode, Sa, Sb, Smp, instantiate_schema, load_certificate, load_frozen_spec,
    schema_metavariables,
)
from lewis_prover.syntax import (
    And, Atom, EquivS, Formula, Neg, Or, Poss, StrictImp, diagnostic_full_erasure,
)

P, Q, R = Atom("p"), Atom("q"), Atom("r")
B1 = StrictImp(And(P, Q), And(Q, P))
BASES = [
    ("S1", "S1_B1_B7", {"B1", "B2", "B3", "B4", "B5", "B6", "B7"}),
    ("S2", "S2_B1_B8", {"B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8"}),
    ("S3", "S3_B1_B7_A8", {"B1", "B2", "B3", "B4", "B5", "B6", "B7", "A8"}),
    ("S4", "S4_B1_B7_C10", {"B1", "B2", "B3", "B4", "B5", "B6", "B7", "C10"}),
    ("S5", "S5_PRIMARY_B1_B7_C11", {"B1", "B2", "B3", "B4", "B5", "B6", "B7", "C11"}),
    ("S5", "S5_ALT_B1_B7_C10_C12", {"B1", "B2", "B3", "B4", "B5", "B6", "B7", "C10", "C12"}),
]
SCHEMAS = ["B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "A8", "C10", "C11", "C12"]


@pytest.fixture(scope="module")
def frozen(repo_root):
    return load_frozen_spec(repo_root)


def certificate(nodes, system="S1", basis="S1_B1_B7"):
    return ProofCertificate("test", system, basis, P, "root", nodes)


def b1():
    return ProofNode(B1, PostulateInstance("B1", {"P": P, "Q": Q}))


def b3(value):
    return ProofNode(StrictImp(value, And(value, value)), PostulateInstance("B3", {"P": value}))


def rejection(checker, node_id, kind, code, reason=None):
    before = dict(checker.accepted_nodes)
    with pytest.raises(NodeCheckError) as caught:
        checker.check_node(node_id)
    error = caught.value
    assert (error.node_id, error.kind, error.code) == (node_id, kind, code)
    assert repr(node_id) in str(error) and kind in str(error) and error.reason
    if reason:
        assert reason in error.reason
    assert dict(checker.accepted_nodes) == before


@pytest.mark.parametrize("schema_id", SCHEMAS)
@pytest.mark.parametrize("system,basis,admitted", BASES)
def test_exact_primitive_admission_in_all_six_bases(frozen, schema_id, system, basis, admitted):
    substitution = {name: Atom(name.lower()) for name in schema_metavariables(schema_id, frozen)}
    node = ProofNode(instantiate_schema(schema_id, substitution, frozen), PostulateInstance(schema_id, substitution))
    checker = NodeChecker(certificate({"post": node}, system, basis), frozen)
    if schema_id in admitted:
        assert checker.check_node("post") == node.conclusion
        assert checker.accepted_nodes["post"] == node.conclusion
    else:
        rejection(checker, "post", "postulate_instance", "SCHEMA_ADMISSION", basis)


@pytest.mark.parametrize("system,basis", [
    ("S5", "S5_UNION_B1_B7_C10_C11_C12"), ("S5", "S1_B1_B7"),
    ("S1", "S5_ALT_B1_B7_C10_C12"), ("S6", "S1_B1_B7"),
    ("S1", ["S1_B1_B7"]), (1, "S1_B1_B7"),
])
def test_union_and_unregistered_basis_pairs_reject(frozen, system, basis):
    checker = NodeChecker(certificate({"post": b1()}, system, basis), frozen)
    rejection(checker, "post", "postulate_instance", "BASIS_IDENTITY")


@pytest.mark.parametrize("schema_id", ["B9", "A7", "DEF_OR", [], None, ""])
def test_unknown_schema_is_never_a_postulate(frozen, schema_id):
    node = ProofNode(B1, PostulateInstance(schema_id, {"P": P, "Q": Q}))
    checker = NodeChecker(certificate({"post": node}), frozen)
    rejection(checker, "post", "postulate_instance", "SCHEMA_ADMISSION")


@pytest.mark.parametrize("substitution,reason", [
    ({"P": P}, "missing"), ({"P": P, "Q": Q, "R": R}, "extra"),
    ({"p": P, "q": Q}, "domain mismatch"),
    ({"P": {"meta": "Q"}, "Q": Q}, "object Formula"),
    ({"P": Formula(), "Q": Q}, "object Formula"),
])
def test_postulate_uses_exact_schema_namespace_and_domain(frozen, substitution, reason):
    checker = NodeChecker(certificate({"post": ProofNode(B1, PostulateInstance("B1", substitution))}), frozen)
    rejection(checker, "post", "postulate_instance", "SCHEMA_INSTANTIATION", reason)


def test_postulate_conclusion_must_be_exact_surface_instance(frozen):
    for conclusion in (P, diagnostic_full_erasure(B1, frozen), StrictImp(And(P, Q), And(Q, R))):
        checker = NodeChecker(certificate({"post": replace(b1(), conclusion=conclusion)}), frozen)
        rejection(checker, "post", "postulate_instance", "CONCLUSION_MISMATCH", "exact surface")


def test_postulate_cannot_smuggle_a_parent_field(frozen):
    data = {
        "proof_id": "test", "system": "S1", "basis_id": "S1_B1_B7", "goal": B1.to_ast(),
        "root": "post", "nodes": {"post": {"conclusion": B1.to_ast(), "justification": {
            "kind": "postulate_instance", "schema_id": "B1", "parents": [],
            "schema_substitution": {"P": P.to_ast(), "Q": Q.to_ast()},
        }}},
    }
    with pytest.raises(CertificateFieldError, match="parents"):
        load_certificate(json.dumps(data), frozen)

    @dataclass(frozen=True)
    class PostulateWithParents(PostulateInstance):
        parents: tuple = ("source",)

    node = ProofNode(B1, PostulateWithParents("B1", {"P": P, "Q": Q}))
    checker = NodeChecker(certificate({"post": node}), frozen)
    rejection(checker, "post", "postulate_instance", "UNSUPPORTED_KIND")


def test_sa_simultaneous_one_pass_trap_and_retry_after_parent_acceptance(frozen):
    expected = StrictImp(And(Q, R), And(R, Q))
    sequential_bug = StrictImp(And(R, R), And(R, R))
    nodes = {
        "sa": ProofNode(expected, Sa(("post",), {"p": Q, "q": R})),
        "bad": ProofNode(sequential_bug, Sa(("post",), {"p": Q, "q": R})),
        "post": b1(),  # serialized/mapping order need not be acceptance order
    }
    checker = NodeChecker(certificate(nodes), frozen)
    rejection(checker, "sa", "Sa", "PARENT_NOT_ACCEPTED", "post")
    assert checker.check_node("post") == B1
    assert checker.check_node("sa") == expected
    rejection(checker, "bad", "Sa", "CONCLUSION_MISMATCH")


@pytest.mark.parametrize("mapping,expected", [
    ({"p": Q, "q": P}, StrictImp(And(Q, P), And(P, Q))),
    ({"p": Neg(P)}, StrictImp(And(Neg(P), Q), And(Q, Neg(P)))),
    ({"p": P}, B1),
])
def test_sa_swap_self_replacement_and_partial_identity(frozen, mapping, expected):
    checker = NodeChecker(certificate({"post": b1(), "sa": ProofNode(expected, Sa(("post",), mapping))}), frozen)
    checker.check_node("post")
    assert checker.check_node("sa") == expected


@pytest.mark.parametrize("mapping,reason", [
    ({}, "nonempty subset"), ({"z": P}, "nonempty subset"),
    ({"p": P, "z": Q}, "nonempty subset"), ({"P": P}, "nonempty subset"),
    ({"p": {"meta": "P"}}, "object Formula"), ({"p": Neg(Formula())}, "object Formula"),
])
def test_sa_invalid_maps_reject_with_transform_reason(frozen, mapping, reason):
    checker = NodeChecker(certificate({"post": b1(), "sa": ProofNode(B1, Sa(("post",), mapping))}), frozen)
    checker.check_node("post")
    rejection(checker, "sa", "Sa", "ATOM_SUBSTITUTION", reason)


def test_direct_schema_instance_is_not_sa_or_implicit_conversion(frozen):
    b2_instance = StrictImp(And(P, Q), P)
    checker = NodeChecker(certificate({
        "post": b1(),
        "b2_as_sa": ProofNode(b2_instance, Sa(("post",), {"p": P})),
        "erased": ProofNode(diagnostic_full_erasure(B1, frozen), Sa(("post",), {"p": P})),
    }), frozen)
    checker.check_node("post")
    rejection(checker, "b2_as_sa", "Sa", "CONCLUSION_MISMATCH")
    rejection(checker, "erased", "Sa", "CONCLUSION_MISMATCH")


@pytest.mark.parametrize("kind", ["Sa", "definition_conversion"])
@pytest.mark.parametrize("parents", [(), ("post", "post"), ("post", "other", "post")])
def test_exact_parent_arity(frozen, kind, parents):
    justification = Sa(parents, {"p": P}) if kind == "Sa" else DefinitionConversion(parents, "DEF_STRICT_IMP", "expand", ())
    checker = NodeChecker(certificate({"post": b1(), "child": ProofNode(B1, justification)}), frozen)
    checker.check_node("post")
    rejection(checker, "child", kind, "PARENT_ARITY", "exactly 1")


@pytest.mark.parametrize("parent,code", [
    ("missing", "PARENT_MISSING"), ("child", "PARENT_NOT_ACCEPTED"),
    ("bad", "PARENT_NOT_ACCEPTED"), ("", "PARENT_REFERENCE"),
    (1, "PARENT_REFERENCE"), (True, "PARENT_REFERENCE"),
])
def test_parent_must_exist_and_have_been_successfully_accepted(frozen, parent, code):
    checker = NodeChecker(certificate({
        "post": b1(), "bad": ProofNode(P, b1().justification),
        "child": ProofNode(B1, Sa((parent,), {"p": P})),
    }), frozen)
    rejection(checker, "bad", "postulate_instance", "CONCLUSION_MISMATCH")
    checker.check_node("post")
    rejection(checker, "child", "Sa", code)


def test_accepted_reference_identity_and_single_parent_choice_are_exact(frozen):
    nodes = {"1": b1(), "01": b3(P), "sa": ProofNode(B1, Sa(("01",), {"p": P}))}
    checker = NodeChecker(certificate(nodes), frozen)
    checker.check_node("1")
    rejection(checker, "sa", "Sa", "PARENT_NOT_ACCEPTED", "01")
    checker.check_node("01")
    rejection(checker, "sa", "Sa", "CONCLUSION_MISMATCH")  # cannot use parent "1"


@pytest.mark.parametrize("definition_id,surface,expanded", [
    ("DEF_OR", Or(P, Q), Neg(And(Neg(P), Neg(Q)))),
    ("DEF_STRICT_IMP", StrictImp(P, Q), Neg(Poss(And(P, Neg(Q))))),
    ("DEF_EQUIV_S", EquivS(P, Q), And(StrictImp(P, Q), StrictImp(Q, P))),
])
def test_all_registered_definition_expansions_and_contractions(frozen, definition_id, surface, expanded):
    parent = b3(surface)
    expected = StrictImp(expanded, And(surface, surface))
    checker = NodeChecker(certificate({
        "post": parent,
        "expand": ProofNode(expected, DefinitionConversion(("post",), definition_id, "expand", ("left",))),
        "contract": ProofNode(parent.conclusion, DefinitionConversion(("expand",), definition_id, "contract", ("left",))),
    }), frozen)
    rejection(checker, "expand", "definition_conversion", "PARENT_NOT_ACCEPTED")
    checker.check_node("post")
    assert checker.check_node("expand") == expected
    assert checker.check_node("contract") == parent.conclusion
    assert frozen.canonical_certificate_contract["kinds"]["definition_conversion"]["is_lewis_inference_rule"] is False


def test_definition_root_conversion(frozen):
    expected = Neg(Poss(And(And(P, Q), Neg(And(Q, P)))))
    checker = NodeChecker(certificate({
        "post": b1(), "convert": ProofNode(expected, DefinitionConversion(("post",), "DEF_STRICT_IMP", "expand", ())),
    }), frozen)
    checker.check_node("post")
    assert checker.check_node("convert") == expected


@pytest.mark.parametrize("definition_id,direction,path,reason", [
    ("DEF_UNKNOWN", "expand", ("left",), "unknown registered definition"),
    ("DEF_EQUIV_S", "left_to_right", ("left",), "direction"),
    ("DEF_EQUIV_S", "expand", ("right",), "does not match"),
    ("DEF_EQUIV_S", "expand", ("name",), "invalid segment"),
    ("DEF_EQUIV_S", "expand", ("left", "left", "arg"), "no traversable child"),
    ("DEF_EQUIV_S", "expand", [["left"], ["right"]], "invalid segment"),
])
def test_definition_id_direction_occurrence_rejections(frozen, definition_id, direction, path, reason):
    parent = b3(EquivS(P, Q))
    checker = NodeChecker(certificate({
        "post": parent,
        "convert": ProofNode(parent.conclusion, DefinitionConversion(("post",), definition_id, direction, path)),
    }), frozen)
    checker.check_node("post")
    rejection(checker, "convert", "definition_conversion", "DEFINITION_CONVERSION", reason)


def test_definition_repeated_metavariable_must_be_structurally_consistent(frozen):
    inconsistent = And(StrictImp(P, Q), StrictImp(Q, R))
    parent = b3(inconsistent)  # legitimate B3 instance, not an assumed parent
    claim = StrictImp(EquivS(P, Q), And(inconsistent, inconsistent))
    checker = NodeChecker(certificate({
        "post": parent,
        "convert": ProofNode(claim, DefinitionConversion(("post",), "DEF_EQUIV_S", "contract", ("left",))),
    }), frozen)
    checker.check_node("post")
    rejection(checker, "convert", "definition_conversion", "DEFINITION_CONVERSION", "repeated")


def test_definition_rejects_hidden_second_or_multiple_occurrence_conversion(frozen):
    surface = EquivS(P, Q)
    expanded = And(StrictImp(P, Q), StrictImp(Q, P))
    correct = StrictImp(expanded, And(surface, surface))
    second_conversion = And(Neg(Poss(And(P, Neg(Q)))), StrictImp(Q, P))
    checker = NodeChecker(certificate({
        "post": b3(surface),
        "good": ProofNode(correct, DefinitionConversion(("post",), "DEF_EQUIV_S", "expand", ("left",))),
        "hidden": ProofNode(StrictImp(second_conversion, And(surface, surface)), DefinitionConversion(("post",), "DEF_EQUIV_S", "expand", ("left",))),
        "multiple": ProofNode(StrictImp(expanded, And(expanded, surface)), DefinitionConversion(("post",), "DEF_EQUIV_S", "expand", ("left",))),
        "erased": ProofNode(diagnostic_full_erasure(correct, frozen), DefinitionConversion(("post",), "DEF_EQUIV_S", "expand", ("left",))),
    }), frozen)
    checker.check_node("post")
    assert checker.check_node("good") == correct
    for node_id in ("hidden", "multiple", "erased"):
        rejection(checker, node_id, "definition_conversion", "CONCLUSION_MISMATCH", "exact surface")


@pytest.mark.parametrize("conclusion", [{"meta": "P"}, {"op": "atom", "name": "p"}, Formula(), Neg(Formula())])
def test_every_checked_conclusion_must_be_an_object_formula(frozen, conclusion):
    checker = NodeChecker(certificate({"post": replace(b1(), conclusion=conclusion)}), frozen)
    rejection(checker, "post", "postulate_instance", "CONCLUSION_FORMULA", "object Formula")


@pytest.mark.parametrize("justification,code", [
    (Sb(("post", "post"), "left_to_right", ()), "SB_EQUIVALENCE_ROOT"),
    (Ad(("post", "post")), "CONCLUSION_MISMATCH"),
    (Smp(("post", "post")), "SMP_ANTECEDENT"),
    (SimpleNamespace(kind="postulate_instance", schema_id="B1"), "UNSUPPORTED_KIND"),
])
def test_invalid_rule_claims_and_unknown_models_reject(frozen, justification, code):
    checker = NodeChecker(certificate({"post": b1(), "unsupported": ProofNode(B1, justification)}), frozen)
    checker.check_node("post")
    rejection(checker, "unsupported", justification.kind, code)


def test_acceptance_ledger_is_read_only_and_scoped_to_one_session(frozen):
    nodes = {"post": b1(), "sa": ProofNode(B1, Sa(("post",), {"p": P}))}
    first = NodeChecker(certificate(nodes, "S1", "S1_B1_B7"), frozen)
    other = NodeChecker(certificate(nodes, "S5", "S5_ALT_B1_B7_C10_C12"), frozen)
    first.check_node("post")
    with pytest.raises(TypeError):
        other.accepted_nodes["post"] = first.accepted_nodes["post"]
    with pytest.raises(AttributeError):
        other.accepted_nodes = first.accepted_nodes
    rejection(other, "sa", "Sa", "PARENT_NOT_ACCEPTED")
    assert other.accepted_nodes == {}
    other.check_node("post")
    assert other.check_node("sa") == B1
    assert first.check_node("post") == B1  # repeat checking is idempotent


def test_serialized_document_to_checked_three_kind_chain(frozen):
    sa_result = StrictImp(And(Q, R), And(R, Q))
    conversion_result = Neg(Poss(And(And(Q, R), Neg(And(R, Q)))))
    data = {
        "proof_id": "integration", "system": "S1", "basis_id": "S1_B1_B7",
        "goal": conversion_result.to_ast(), "root": "convert", "nodes": {
            "post": {"conclusion": B1.to_ast(), "justification": {"kind": "postulate_instance", "schema_id": "B1",
                "schema_substitution": {"P": P.to_ast(), "Q": Q.to_ast()}}},
            "sa": {"conclusion": sa_result.to_ast(), "justification": {"kind": "Sa", "parents": ["post"],
                "atom_substitution": {"p": Q.to_ast(), "q": R.to_ast()}}},
            "convert": {"conclusion": conversion_result.to_ast(), "justification": {"kind": "definition_conversion",
                "parents": ["sa"], "definition_id": "DEF_STRICT_IMP", "direction": "expand", "occurrence_path": []}},
        },
    }
    cert = load_certificate(json.dumps(data).encode("utf-8"), frozen)
    checker = NodeChecker(cert, frozen)
    for node_id in ("post", "sa", "convert"):
        checker.check_node(node_id)
    assert checker.accepted_nodes[cert.root] == cert.goal
    assert len(checker.accepted_nodes) == 3


def test_node_lookup_reports_identifier_and_reason(frozen):
    checker = NodeChecker(certificate({"post": b1()}), frozen)
    rejection(checker, "absent", "<missing>", "NODE_MISSING")
    for node_id in ("", 1, None, []):
        rejection(checker, node_id, "<unknown>", "NODE_ID")
