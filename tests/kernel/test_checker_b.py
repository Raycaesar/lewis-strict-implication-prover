"""Lewis-operation checks using actual accepted parent derivations."""

import json
from types import SimpleNamespace

import pytest

from lewis_prover.errors import CertificateStructureError, NodeCheckError
from lewis_prover.kernel import (
    Ad, DefinitionConversion, NodeChecker, PostulateInstance, ProofCertificate,
    ProofNode, Sb, Smp, load_certificate, load_frozen_spec,
)
from lewis_prover.syntax import (
    And, Atom, EquivS, Neg, Or, Poss, StrictImp, diagnostic_full_erasure,
)

P, Q, R = Atom("p"), Atom("q"), Atom("r")


@pytest.fixture(scope="module")
def frozen(repo_root):
    return load_frozen_spec(repo_root)


def certificate(nodes, system="S1", basis_id="S1_B1_B7"):
    return ProofCertificate("lewis-operations", system, basis_id, P, "root", nodes)


def b1(left=P, right=Q):
    return ProofNode(
        StrictImp(And(left, right), And(right, left)),
        PostulateInstance("B1", {"P": left, "Q": right}),
    )


def b3(value=P):
    return ProofNode(StrictImp(value, And(value, value)), PostulateInstance("B3", {"P": value}))


def commutation(left=P, right=Q):
    """Derive (left and right) equiv_s (right and left) via B1/Ad/definition."""
    forward, reverse = b1(left, right), b1(right, left)
    mutual = And(forward.conclusion, reverse.conclusion)
    return {
        "forward": forward,
        "reverse": reverse,
        "mutual": ProofNode(mutual, Ad(("forward", "reverse"))),
        "equivalence": ProofNode(
            EquivS(And(left, right), And(right, left)),
            DefinitionConversion(("mutual",), "DEF_EQUIV_S", "contract", ()),
        ),
    }


def accept(checker, *node_ids):
    for node_id in node_ids:
        checker.check_node(node_id)


def reject(checker, node_id, kind, code, reason=None):
    before = dict(checker.accepted_nodes)
    with pytest.raises(NodeCheckError) as caught:
        checker.check_node(node_id)
    error = caught.value
    assert (error.node_id, error.kind, error.code) == (node_id, kind, code)
    assert error.reason and repr(node_id) in str(error) and kind in str(error)
    if reason:
        assert reason in error.reason
    assert dict(checker.accepted_nodes) == before


@pytest.mark.parametrize("direction", ["left_to_right", "right_to_left"])
def test_sb_both_directions_require_the_explicitly_contracted_equivalence(frozen, direction):
    left, right = And(P, Q), And(Q, P)
    source, replacement = (left, right) if direction == "left_to_right" else (right, left)
    result = StrictImp(replacement, And(source, source))
    nodes = commutation()
    nodes.update({
        "target": b3(source),
        "bad": ProofNode(result, Sb(("mutual", "target"), direction, ("left",))),
        "good": ProofNode(result, Sb(("equivalence", "target"), direction, ("left",))),
    })
    checker = NodeChecker(certificate(nodes), frozen)
    accept(checker, "forward", "reverse", "mutual", "target")
    reject(checker, "bad", "Sb", "SB_EQUIVALENCE_ROOT", "literal surface equiv_s")
    reject(checker, "good", "Sb", "PARENT_NOT_ACCEPTED", "equivalence")
    checker.check_node("equivalence")
    assert checker.check_node("good") == result


def test_sb_changes_one_occurrence_even_when_three_subtrees_are_shared(frozen):
    left, right = And(P, Q), And(Q, P)
    correct = StrictImp(right, And(left, left))
    nodes = commutation()
    nodes.update({
        "target": b3(left),
        "good": ProofNode(correct, Sb(("equivalence", "target"), "left_to_right", ("left",))),
        "two": ProofNode(StrictImp(right, And(right, left)), Sb(("equivalence", "target"), "left_to_right", ("left",))),
        "all": ProofNode(StrictImp(right, And(right, right)), Sb(("equivalence", "target"), "left_to_right", ("left",))),
    })
    checker = NodeChecker(certificate(nodes), frozen)
    accept(checker, "forward", "reverse", "mutual", "equivalence", "target")
    result = checker.check_node("good")
    assert result == correct
    target = nodes["target"].conclusion
    assert result.right == target.right
    assert target.left is target.right.left is target.right.right
    reject(checker, "two", "Sb", "CONCLUSION_MISMATCH")
    reject(checker, "all", "Sb", "CONCLUSION_MISMATCH")


@pytest.mark.parametrize("wrapper,path", [
    (Neg, ("left", "arg")), (Poss, ("left", "arg")),
    (lambda value: Or(value, R), ("left", "left")),
    (lambda value: EquivS(R, value), ("left", "right")),
])
def test_sb_preserves_unselected_defined_and_primitive_contexts(frozen, wrapper, path):
    left, right = And(P, Q), And(Q, P)
    target = b3(wrapper(left))
    result = StrictImp(wrapper(right), And(wrapper(left), wrapper(left)))
    nodes = commutation()
    nodes.update(target=target, sb=ProofNode(result, Sb(("equivalence", "target"), "left_to_right", path)))
    checker = NodeChecker(certificate(nodes), frozen)
    accept(checker, "forward", "reverse", "mutual", "equivalence", "target")
    assert checker.check_node("sb") == result


def test_sb_root_replacement_on_an_accepted_target(frozen):
    left, right = b1().conclusion, b3().conclusion
    nodes = commutation(left, right)
    nodes.update({
        "a": b1(), "b": b3(),
        "target": ProofNode(And(left, right), Ad(("a", "b"))),
        "sb": ProofNode(And(right, left), Sb(("equivalence", "target"), "left_to_right", ())),
    })
    checker = NodeChecker(certificate(nodes), frozen)
    accept(checker, "a", "b", "target", "forward", "reverse", "mutual", "equivalence")
    assert checker.check_node("sb") == And(right, left)


@pytest.mark.parametrize("direction,path,code", [
    ("wrong", ("left",), "SB_DIRECTION"), ("expand", ("left",), "SB_DIRECTION"),
    ([], ("left",), "SB_DIRECTION"), ("right_to_left", ("left",), "SB_SOURCE_MATCH"),
    ("left_to_right", ("left", "left"), "SB_SOURCE_MATCH"),
    ("left_to_right", ("arg",), "SB_REPLACEMENT"),
    ("left_to_right", ("name",), "SB_REPLACEMENT"),
    ("left_to_right", ("left", "left", "arg"), "SB_REPLACEMENT"),
    ("left_to_right", [["left"], ["right"]], "SB_REPLACEMENT"),
])
def test_sb_wrong_direction_or_path(frozen, direction, path, code):
    nodes = commutation()
    nodes.update(target=b3(And(P, Q)), bad=ProofNode(P, Sb(("equivalence", "target"), direction, path)))
    checker = NodeChecker(certificate(nodes), frozen)
    accept(checker, "forward", "reverse", "mutual", "equivalence", "target")
    reject(checker, "bad", "Sb", code)


def test_sb_parent_roles_are_ordered(frozen):
    nodes = commutation()
    nodes.update(target=b3(And(P, Q)), bad=ProofNode(P, Sb(("target", "equivalence"), "left_to_right", ("left",))))
    checker = NodeChecker(certificate(nodes), frozen)
    accept(checker, "forward", "reverse", "mutual", "equivalence", "target")
    reject(checker, "bad", "Sb", "SB_EQUIVALENCE_ROOT")


def test_sb_cannot_rescue_a_source_match_by_definition_expansion(frozen):
    defined = StrictImp(P, Q)
    expanded = Neg(Poss(And(P, Neg(Q))))
    nodes = commutation(defined, R)
    nodes.update({
        "target": b3(And(expanded, R)),
        "bad": ProofNode(P, Sb(("equivalence", "target"), "left_to_right", ("left",))),
    })
    checker = NodeChecker(certificate(nodes), frozen)
    accept(checker, "forward", "reverse", "mutual", "equivalence", "target")
    reject(checker, "bad", "Sb", "SB_SOURCE_MATCH")


def test_ad_conclusion_is_exactly_the_given_parent_order(frozen):
    first, second = b1(), b3()
    nodes = {
        "a": first, "b": second,
        "ordered": ProofNode(And(first.conclusion, second.conclusion), Ad(("a", "b"))),
        "swapped": ProofNode(And(second.conclusion, first.conclusion), Ad(("a", "b"))),
        "reversed": ProofNode(And(second.conclusion, first.conclusion), Ad(("b", "a"))),
        "repeated": ProofNode(And(first.conclusion, first.conclusion), Ad(("a", "a"))),
    }
    checker = NodeChecker(certificate(nodes), frozen)
    accept(checker, "a", "b")
    accept(checker, "ordered", "reversed", "repeated")
    reject(checker, "swapped", "Ad", "CONCLUSION_MISMATCH")


def test_ad_no_reassociation_or_implicit_definition_conversion(frozen):
    first, second, third = b1(), b3(), b3(Q)
    a, b, c = first.conclusion, second.conclusion, third.conclusion
    nodes = {
        "a": first, "b": second, "c": third,
        "ab": ProofNode(And(a, b), Ad(("a", "b"))),
        "good": ProofNode(And(And(a, b), c), Ad(("ab", "c"))),
        "reassociated": ProofNode(And(a, And(b, c)), Ad(("ab", "c"))),
        "erased": ProofNode(diagnostic_full_erasure(And(a, b), frozen), Ad(("a", "b"))),
    }
    checker = NodeChecker(certificate(nodes), frozen)
    accept(checker, "a", "b", "c", "ab", "good")
    reject(checker, "reassociated", "Ad", "CONCLUSION_MISMATCH")
    reject(checker, "erased", "Ad", "CONCLUSION_MISMATCH")

    nodes = commutation()
    nodes["implicit_equivalence"] = ProofNode(nodes["equivalence"].conclusion, Ad(("forward", "reverse")))
    checker = NodeChecker(certificate(nodes), frozen)
    accept(checker, "forward", "reverse")
    reject(checker, "implicit_equivalence", "Ad", "CONCLUSION_MISMATCH")


def test_smp_detaches_the_exact_surface_consequent(frozen):
    theorem = b1()
    t = theorem.conclusion
    nodes = {
        "theorem": theorem, "implication": b3(t),
        "smp": ProofNode(And(t, t), Smp(("theorem", "implication"))),
        "wrong_conclusion": ProofNode(t, Smp(("theorem", "implication"))),
        "reversed": ProofNode(And(t, t), Smp(("implication", "theorem"))),
    }
    checker = NodeChecker(certificate(nodes), frozen)
    accept(checker, "theorem", "implication")
    assert checker.check_node("smp") == And(t, t)
    reject(checker, "wrong_conclusion", "Smp", "CONCLUSION_MISMATCH")
    reject(checker, "reversed", "Smp", "SMP_ANTECEDENT")


def test_smp_works_with_a_surface_conjunction_antecedent(frozen):
    first, second = b1(), b3()
    a, b = first.conclusion, second.conclusion
    nodes = {
        "a": first, "b": second,
        "antecedent": ProofNode(And(a, b), Ad(("a", "b"))),
        "implication": ProofNode(StrictImp(And(a, b), a), PostulateInstance("B2", {"P": a, "Q": b})),
        "smp": ProofNode(a, Smp(("antecedent", "implication"))),
        "wrong_root": ProofNode(a, Smp(("a", "antecedent"))),
    }
    checker = NodeChecker(certificate(nodes), frozen)
    accept(checker, "a", "b", "antecedent", "implication")
    assert checker.check_node("smp") == a
    reject(checker, "wrong_root", "Smp", "SMP_IMPLICATION_ROOT")


def test_smp_rejects_erasure_equality_in_premise_root_antecedent_and_conclusion(frozen):
    theorem = b1()
    t = theorem.conclusion
    expanded_t = Neg(Poss(And(t.left, Neg(t.right))))
    implication = StrictImp(t, And(t, t))
    expanded_implication = Neg(Poss(And(t, Neg(And(t, t)))))
    nodes = {
        "t": theorem, "implication": b3(t),
        "expanded_t": ProofNode(expanded_t, DefinitionConversion(("t",), "DEF_STRICT_IMP", "expand", ())),
        "expanded_implication": ProofNode(expanded_implication, DefinitionConversion(("implication",), "DEF_STRICT_IMP", "expand", ())),
        "antecedent_trap": ProofNode(And(t, t), Smp(("expanded_t", "implication"))),
        "root_trap": ProofNode(And(t, t), Smp(("t", "expanded_implication"))),
        "conclusion_trap": ProofNode(diagnostic_full_erasure(And(t, t), frozen), Smp(("t", "implication"))),
    }
    assert diagnostic_full_erasure(t, frozen) == diagnostic_full_erasure(expanded_t, frozen)
    assert diagnostic_full_erasure(implication, frozen) == diagnostic_full_erasure(expanded_implication, frozen)
    checker = NodeChecker(certificate(nodes), frozen)
    accept(checker, "t", "implication", "expanded_t", "expanded_implication")
    reject(checker, "antecedent_trap", "Smp", "SMP_ANTECEDENT")
    reject(checker, "root_trap", "Smp", "SMP_IMPLICATION_ROOT")
    reject(checker, "conclusion_trap", "Smp", "CONCLUSION_MISMATCH")


@pytest.mark.parametrize("kind", ["Sb", "Ad", "Smp"])
@pytest.mark.parametrize("parents", [(), ("post",), ("post", "post", "post")])
def test_two_ordered_parents_required(frozen, kind, parents):
    justification = {"Sb": lambda: Sb(parents, "left_to_right", ()), "Ad": lambda: Ad(parents), "Smp": lambda: Smp(parents)}[kind]()
    checker = NodeChecker(certificate({"post": b1(), "bad": ProofNode(P, justification)}), frozen)
    checker.check_node("post")
    reject(checker, "bad", kind, "PARENT_ARITY", "exactly 2")


@pytest.mark.parametrize("kind", ["Sb", "Ad", "Smp"])
@pytest.mark.parametrize("parent,code", [
    ("pending", "PARENT_NOT_ACCEPTED"), ("missing", "PARENT_MISSING"),
    ("bad", "PARENT_NOT_ACCEPTED"), (1, "PARENT_REFERENCE"), ("", "PARENT_REFERENCE"),
])
@pytest.mark.parametrize("position", [0, 1])
def test_both_parents_must_exist_and_be_accepted(frozen, kind, parent, code, position):
    parents = ["post", "post"]
    parents[position] = parent
    justification = {"Sb": lambda: Sb(parents, "left_to_right", ()), "Ad": lambda: Ad(parents), "Smp": lambda: Smp(parents)}[kind]()
    checker = NodeChecker(certificate({"post": b1(), "pending": b3(), "bad": ProofNode(P, justification)}), frozen)
    checker.check_node("post")
    reject(checker, "bad", kind, code)


@pytest.mark.parametrize("kind", ["material_modus_ponens", "unrestricted_necessitation", "system_inclusion", "s5_bridge", "semantic_validity"])
def test_modern_rules_and_bridge_macros_are_not_certificate_kinds(frozen, kind):
    checker = NodeChecker(certificate({"post": b1(), "bad": ProofNode(P, SimpleNamespace(kind=kind))}), frozen)
    checker.check_node("post")
    reject(checker, "bad", kind, "UNSUPPORTED_KIND")


@pytest.mark.parametrize("op", ["material_imp", "box", "="])
def test_forbidden_formula_operators_cannot_reach_a_logical_rule(frozen, op):
    formula = {"op": op, "left": P.to_ast(), "right": Q.to_ast()}
    data = {
        "proof_id": "forbidden", "system": "S1", "basis_id": "S1_B1_B7",
        "goal": P.to_ast(), "root": "bad", "nodes": {
            "bad": {"conclusion": formula, "justification": {"kind": "Smp", "parents": ["a", "b"]}},
        },
    }
    with pytest.raises(CertificateStructureError):
        load_certificate(json.dumps(data), frozen)


def test_serialized_b1_ad_definition_sb_smp_chain(frozen):
    left, right = b1().conclusion, b3().conclusion
    nodes = commutation(left, right)
    nodes.update({
        "a": b1(), "b": b3(),
        "target": ProofNode(And(left, right), Ad(("a", "b"))),
        "sb": ProofNode(And(right, left), Sb(("equivalence", "target"), "left_to_right", ())),
        "b2": ProofNode(StrictImp(And(right, left), right), PostulateInstance("B2", {"P": right, "Q": left})),
        "smp": ProofNode(right, Smp(("sb", "b2"))),
    })
    from dataclasses import fields

    def justification_ast(justification):
        result = {"kind": justification.kind}
        for field in fields(justification):
            value = getattr(justification, field.name)
            if field.name == "schema_substitution":
                value = {key: formula.to_ast() for key, formula in value.items()}
            result[field.name] = value
        return result

    data = {"proof_id": "chain", "system": "S1", "basis_id": "S1_B1_B7", "goal": right.to_ast(), "root": "smp", "nodes": {
        node_id: {"conclusion": node.conclusion.to_ast(), "justification": justification_ast(node.justification)}
        for node_id, node in nodes.items()
    }}
    loaded = load_certificate(json.dumps(data).encode(), frozen)
    checker = NodeChecker(loaded, frozen)
    accept(checker, "forward", "reverse", "mutual", "equivalence", "a", "b", "target", "sb", "b2", "smp")
    assert checker.accepted_nodes[loaded.root] == loaded.goal
