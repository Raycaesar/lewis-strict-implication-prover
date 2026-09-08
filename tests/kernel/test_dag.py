"""Complete serialized-boundary checks, graph witnesses, and stable diagnostics."""

import copy
from dataclasses import FrozenInstanceError, fields
import json
import random

import pytest

from lewis_prover.errors import CertificateValidationError
from lewis_prover.kernel import (
    Ad, CheckedCertificate, DefinitionConversion, PostulateInstance, ProofNode,
    Sa, Sb, Smp, check_certificate, instantiate_schema, linearize, load_frozen_spec,
)
from lewis_prover.syntax import And, Atom, EquivS, Poss, StrictImp, diagnostic_full_erasure

P, Q = Atom("p"), Atom("q")


@pytest.fixture(scope="module")
def frozen(repo_root):
    return load_frozen_spec(repo_root)


def post(frozen, schema_id="B3", substitution=None):
    substitution = {"P": P} if substitution is None else substitution
    return ProofNode(instantiate_schema(schema_id, substitution, frozen), PostulateInstance(schema_id, substitution))


def node_ast(node):
    justification = {"kind": node.justification.kind}
    for field in fields(node.justification):
        value = getattr(node.justification, field.name)
        if field.name in ("schema_substitution", "atom_substitution"):
            value = {name: formula.to_ast() for name, formula in value.items()}
        elif isinstance(value, tuple):
            value = list(value)
        justification[field.name] = value
    return {"conclusion": node.conclusion.to_ast(), "justification": justification}


def document(nodes, root, *, system="S1", basis_id="S1_B1_B7", goal=None):
    return {
        "proof_id": "test", "system": system, "basis_id": basis_id,
        "root": root, "goal": (nodes[root].conclusion if goal is None else goal).to_ast(),
        "nodes": {node_id: node_ast(node) for node_id, node in nodes.items()},
    }


def check(data, frozen):
    return check_certificate(json.dumps(data).encode("utf-8"), frozen)


def reject(data, frozen, code, node_id=None, kind=None):
    with pytest.raises(CertificateValidationError) as caught:
        check(data, frozen)
    error = caught.value
    assert error.code == code
    assert error.reason
    if node_id is not None:
        assert error.node_id == node_id
    if kind is not None:
        assert error.kind == kind
    return error


@pytest.fixture
def complete_document(frozen):
    """A root-connected DAG using all six kinds, including shared parents."""
    a = post(frozen, "B1", {"P": Poss(P), "Q": Q})
    b = post(frozen)
    left, right = a.conclusion, b.conclusion
    forward = post(frozen, "B1", {"P": left, "Q": right})
    reverse = post(frozen, "B1", {"P": right, "Q": left})
    nodes = {
        "a": a, "b": b, "forward": forward, "reverse": reverse,
        "mutual": ProofNode(And(forward.conclusion, reverse.conclusion), Ad(("forward", "reverse"))),
        "equivalence": ProofNode(EquivS(And(left, right), And(right, left)),
                                 DefinitionConversion(("mutual",), "DEF_EQUIV_S", "contract", ())),
        "target": ProofNode(And(left, right), Ad(("a", "b"))),
        "sb": ProofNode(And(right, left), Sb(("equivalence", "target"), "left_to_right", ())),
        "b2": post(frozen, "B2", {"P": right, "Q": left}),
        "smp": ProofNode(right, Smp(("sb", "b2"))),
        "root": ProofNode(StrictImp(Poss(P), And(Poss(P), Poss(P))), Sa(("smp",), {"p": Poss(P)})),
    }
    return document(nodes, "root")


@pytest.mark.parametrize("system,basis_id,schema_id", [
    ("S1", "S1_B1_B7", "B3"), ("S2", "S2_B1_B8", "B3"),
    ("S3", "S3_B1_B7_A8", "A8"), ("S4", "S4_B1_B7_C10", "C10"),
    ("S5", "S5_PRIMARY_B1_B7_C11", "C11"),
    ("S5", "S5_ALT_B1_B7_C10_C12", "C10"),
    ("S5", "S5_ALT_B1_B7_C10_C12", "C12"),
])
def test_single_node_all_bases(frozen, system, basis_id, schema_id):
    # A8 uses both P and Q; other schemas here use only P.
    env = {"P": P, "Q": Q} if schema_id == "A8" else {"P": P}
    data = document({"non-numeric ID": post(frozen, schema_id, env)}, "non-numeric ID", system=system, basis_id=basis_id)
    checked = check(data, frozen)
    assert type(checked) is CheckedCertificate
    assert linearize(checked) == ("non-numeric ID",)
    assert checked.certificate.nodes[checked.certificate.root].conclusion == checked.certificate.goal


def test_all_six_kinds_are_checked_parent_first_once(frozen, complete_document, monkeypatch):
    from lewis_prover.kernel.checker import NodeChecker

    original = NodeChecker.check_node
    calls = []

    def observed(self, node_id):
        calls.append(node_id)
        return original(self, node_id)

    monkeypatch.setattr(NodeChecker, "check_node", observed)
    checked = check(complete_document, frozen)
    assert calls == list(linearize(checked))
    assert len(set(calls)) == len(calls) == len(complete_document["nodes"])
    assert calls[-1] == "root"
    for node_id, node in complete_document["nodes"].items():
        for parent in node["justification"].get("parents", []):
            assert calls.index(parent) < calls.index(node_id)
    with pytest.raises(FrozenInstanceError):
        checked.node_order = ()
    with pytest.raises(TypeError):
        checked.certificate.nodes["extra"] = checked.certificate.nodes["a"]


def test_repeated_parent_edges_are_not_duplicate_nodes(frozen):
    a = post(frozen)
    data = document({"a": a, "root": ProofNode(And(a.conclusion, a.conclusion), Ad(("a", "a")))}, "root")
    assert linearize(check(data, frozen)) == ("a", "root")


@pytest.mark.parametrize("payload", [
    b'{"root":"a","root":"b"}', b'{"nodes":{"a":{},"\\u0061":{}}}',
    b'{"nodes":{"a":{"justification":{"kind":"Sa","kind":"Ad"}}}}',
    b'{"op":"atom","name":"p","name":"q"}', b'\xff', b'\xef\xbb\xbf{}',
    b'{"x":"\\ud800"}', b'{"x":NaN}', b'{"x":Infinity}', b'{"x":-Infinity}',
    b'{"x":1}', b'{"x":true}', b'{"x":null}', b'[]', b'{',
])
def test_document_errors_precede_all_logical_validation(frozen, payload, monkeypatch):
    from lewis_prover.kernel import dag

    def forbidden(*args):
        pytest.fail("logical validation began before successful strict decoding")

    monkeypatch.setattr(dag, "_graph_order", forbidden)
    with pytest.raises(CertificateValidationError) as caught:
        check_certificate(payload, frozen)
    assert caught.value.code == "document_decode_error"
    assert caught.value.detail_code


def test_mapping_or_model_cannot_bypass_duplicate_detection(frozen):
    data = document({"root": post(frozen)}, "root")
    for value in (data, check(data, frozen).certificate, check(data, frozen)):
        with pytest.raises(CertificateValidationError) as caught:
            check_certificate(value, frozen)
        assert caught.value.code == "document_decode_error"


@pytest.mark.parametrize("location", ["proof", "node", "justification"])
def test_closed_world_fields_have_stable_code(frozen, location):
    data = document({"root": post(frozen)}, "root")
    target = {"proof": data, "node": data["nodes"]["root"],
              "justification": data["nodes"]["root"]["justification"]}[location]
    target["line_number"] = "1"
    reject(data, frozen, "closed_world_field_error")


@pytest.mark.parametrize("location", ["goal", "conclusion", "substitution"])
@pytest.mark.parametrize("formula", [{"op": "box", "arg": P.to_ast()}, {"meta": "P"}, {"op": "atom", "name": "p", "extra": "x"}])
def test_invalid_formula_code_at_every_formula_boundary(frozen, location, formula):
    data = document({"root": post(frozen)}, "root")
    if location == "goal":
        data["goal"] = formula
    elif location == "conclusion":
        data["nodes"]["root"]["conclusion"] = formula
    else:
        data["nodes"]["root"]["justification"]["schema_substitution"]["P"] = formula
    reject(data, frozen, "invalid_formula")


@pytest.mark.parametrize("system,basis", [("S1", "S2_B1_B8"), ("S5", "S5_UNION_B1_B7_C10_C11_C12"), ("s1", "S1_B1_B7")])
def test_invalid_basis_code(frozen, system, basis):
    reject(document({"root": post(frozen)}, "root", system=system, basis_id=basis), frozen, "invalid_basis")


@pytest.mark.parametrize("basis,forbidden", [("S5_PRIMARY_B1_B7_C11", "C10"), ("S5_ALT_B1_B7_C10_C12", "C11")])
def test_every_postulate_is_basis_specific(frozen, basis, forbidden):
    data = document({"root": post(frozen, forbidden)}, "root", system="S5", basis_id=basis)
    error = reject(data, frozen, "invalid_postulate_instance", "root", "postulate_instance")
    assert error.detail_code == "SCHEMA_ADMISSION"


@pytest.mark.parametrize("root", ["absent", "01", "ROOT"])
def test_root_must_resolve_exactly(frozen, root):
    data = document({"root": post(frozen)}, "root")
    data["root"] = root
    reject(data, frozen, "missing_root", root)


def test_empty_node_map_has_no_root(frozen):
    data = document({"root": post(frozen)}, "root")
    data["nodes"] = {}
    reject(data, frozen, "missing_root", "root")


@pytest.mark.parametrize("target", ["proof_id", "root", "node_id", "parent"])
def test_nonempty_identifiers_required(frozen, target):
    a = post(frozen)
    data = document({"a": a, "root": ProofNode(a.conclusion, Sa(("a",), {"p": P}))}, "root")
    if target == "node_id":
        data["nodes"][""] = data["nodes"].pop("a")
    elif target == "parent":
        data["nodes"]["root"]["justification"]["parents"] = [""]
    else:
        data[target] = ""
    reject(data, frozen, "invalid_identifier")


@pytest.mark.parametrize("source,reference", [("a", "A"), ("a", " a"), ("1", "01"), ("é", "e\u0301")])
def test_missing_parent_uses_exact_string_identity(frozen, source, reference):
    a = post(frozen)
    data = document({source: a, "root": ProofNode(a.conclusion, Sa((reference,), {"p": P}))}, "root")
    error = reject(data, frozen, "missing_parent", "root", "Sa")
    assert error.related_ids == (reference,)


def test_numeric_reference_is_not_a_line_number(frozen):
    a = post(frozen)
    data = document({"1": a, "root": ProofNode(a.conclusion, Sa(("1",), {"p": P}))}, "root")
    assert linearize(check(data, frozen)) == ("1", "root")
    data["nodes"]["root"]["justification"]["parents"] = [1]
    reject(data, frozen, "document_decode_error")


@pytest.mark.parametrize("cyclic_nodes", [("a",), ("a", "b"), ("a", "b", "c")])
def test_cycles_report_a_deterministic_closed_witness(frozen, cyclic_nodes):
    formula = post(frozen).conclusion
    nodes = {node_id: ProofNode(formula, Sa((cyclic_nodes[(i + 1) % len(cyclic_nodes)],), {"p": P}))
             for i, node_id in enumerate(cyclic_nodes)}
    error = reject(document(nodes, "a"), frozen, "cycle")
    assert error.related_ids == cyclic_nodes + ("a",)


def test_cycle_in_disconnected_component_is_not_ignored(frozen):
    a = post(frozen)
    nodes = {"root": a, "garbage": ProofNode(a.conclusion, Sa(("garbage",), {"p": P}))}
    reject(document(nodes, "root"), frozen, "cycle", "garbage")


def test_unreachable_nodes_even_valid_theorems_are_rejected(frozen):
    nodes = {"root": post(frozen), "z": post(frozen), "a": post(frozen)}
    error = reject(document(nodes, "root"), frozen, "unreachable_node", "a")
    assert error.related_ids == ("a", "z")


def test_root_goal_surface_equality_not_erasure(frozen):
    a = post(frozen)
    reject(document({"root": a}, "root", goal=P), frozen, "root_goal_mismatch", "root")
    reject(document({"root": a}, "root", goal=diagnostic_full_erasure(a.conclusion, frozen)),
           frozen, "root_goal_mismatch", "root")


@pytest.mark.parametrize("node_id,kind", [
    ("a", "postulate_instance"), ("root", "Sa"), ("sb", "Sb"),
    ("target", "Ad"), ("smp", "Smp"), ("equivalence", "definition_conversion"),
])
def test_all_six_logical_failure_codes(frozen, complete_document, node_id, kind):
    complete_document["nodes"][node_id]["conclusion"] = P.to_ast()
    error = reject(complete_document, frozen, "invalid_" + kind, node_id, kind)
    assert error.detail_code == "CONCLUSION_MISMATCH"


@pytest.mark.parametrize("node_id", ["root", "sb", "target", "smp", "equivalence"])
def test_structurally_invalid_rule_payloads_have_kind_codes(frozen, complete_document, node_id):
    justification = complete_document["nodes"][node_id]["justification"]
    justification["parents"] = []
    reject(complete_document, frozen, "invalid_" + justification["kind"], node_id, justification["kind"])


def shuffled_objects(value, rng):
    if isinstance(value, dict):
        items = list(value.items())
        rng.shuffle(items)
        return {key: shuffled_objects(child, rng) for key, child in items}
    if isinstance(value, list):
        return [shuffled_objects(child, rng) for child in value]
    return value


def test_linearization_is_stable_across_repeated_runs_and_object_orders(frozen, complete_document):
    expected = linearize(check(complete_document, frozen))
    for seed in range(20):
        assert linearize(check(shuffled_objects(complete_document, random.Random(seed)), frozen)) == expected


@pytest.mark.parametrize("failure", ["structure", "missing", "cycle", "unreachable", "rule"])
def test_first_error_is_deterministic_across_node_map_orders(frozen, failure):
    a = post(frozen)
    nodes = {"a": a, "z": a, "root": ProofNode(And(a.conclusion, a.conclusion), Ad(("a", "z")))}
    data = document(nodes, "root")
    for node_id in ("a", "z"):
        node = data["nodes"][node_id]
        if failure == "structure":
            node["extra"] = "forbidden"
        elif failure in ("missing", "cycle"):
            node["justification"] = {"kind": "Sa", "parents": [node_id if failure == "cycle" else "missing"],
                                     "atom_substitution": {"p": P.to_ast()}}
        elif failure == "rule":
            node["conclusion"] = P.to_ast()
    if failure == "unreachable":
        data["nodes"]["root"] = node_ast(a)
    signatures = set()
    for seed in range(10):
        with pytest.raises(CertificateValidationError) as caught:
            check(shuffled_objects(data, random.Random(seed)), frozen)
        error = caught.value
        signatures.add((error.code, error.node_id, error.kind, error.detail_code, error.related_ids, str(error)))
    assert len(signatures) == 1


def test_iterative_graph_traversal_handles_long_shallow_formula_chain(frozen):
    a = post(frozen)
    # The lexically first ID is the root, forcing one 1,500-deep DFS traversal.
    nodes = {"1499": a}
    for index in reversed(range(1499)):
        nodes[f"{index:04d}"] = ProofNode(a.conclusion, Sa((f"{index + 1:04d}",), {"p": P}))
    checked = check(document(nodes, "0000"), frozen)
    assert linearize(checked) == tuple(nodes)


def test_input_and_success_are_not_changed_by_validation(frozen, complete_document):
    before = copy.deepcopy(complete_document)
    first = check(complete_document, frozen)
    second = check(complete_document, frozen)
    assert complete_document == before
    assert first == second


def test_lewis_renderer_preserves_all_six_kinds_and_surface_notation(frozen, complete_document):
    from lewis_prover.render import render_proof

    checked = check(complete_document, frozen)
    rendered = render_proof(checked)
    for token in ("⥽", "≡ₛ", "◇", "Df DEF_EQUIV_S contract", "B1", "B2", "B3", "Sa ", "Sb ", "Ad ", "Smp "):
        assert token in rendered
    for seed in range(10):
        reordered = shuffled_objects(complete_document, random.Random(seed))
        assert render_proof(check(reordered, frozen)) == rendered
    assert check(complete_document, frozen) == checked


@pytest.mark.parametrize("schema_id,system,basis_id,env", [
    ("B3", "S1", "S1_B1_B7", {"P": P}),
    ("A8", "S3", "S3_B1_B7_A8", {"P": P, "Q": Q}),
    ("C11", "S5", "S5_PRIMARY_B1_B7_C11", {"P": P}),
])
def test_renderer_keeps_registered_b_a_c_schema_labels(frozen, schema_id, system, basis_id, env):
    from lewis_prover.render import render_proof

    data = document({"root": post(frozen, schema_id, env)}, "root", system=system, basis_id=basis_id)
    assert f"    {schema_id} {{" in render_proof(check(data, frozen))


def test_line_numbering_is_only_rendering_and_preserves_parent_order(frozen):
    from lewis_prover.render import render_proof

    a, b = post(frozen), post(frozen, "B3", {"P": Q})
    nodes = {"90": a, "3": b, "1": ProofNode(And(a.conclusion, b.conclusion), Ad(("90", "3")))}
    data = document(nodes, "1")
    checked = check(data, frozen)
    assert linearize(checked) == ("90", "3", "1")  # DFS parent order, not numeric sorting.
    normal = render_proof(checked)
    offset = render_proof(checked, first_line=100)
    assert "Ad 1, 2" in normal and "Ad 100, 101" in offset
    assert "root line 3" in normal and "root line 102" in offset
    assert normal != offset and check(data, frozen) == checked
    with pytest.raises(CertificateValidationError) as caught:
        check_certificate(normal, frozen)
    assert caught.value.code == "document_decode_error"
    # Replacing a logical ID with its displayed line number does not resolve it.
    data["nodes"]["1"]["justification"]["parents"] = ["100", "101"]
    reject(data, frozen, "missing_parent", "1")


def test_renderer_changes_or_failures_do_not_participate_in_acceptance(frozen, complete_document, monkeypatch):
    from lewis_prover import render

    accepted = check(complete_document, frozen)
    monkeypatch.setattr(render, "pretty_formula", lambda formula: "deliberately misleading presentation")
    assert "deliberately misleading presentation" in render.render_proof(accepted)
    assert check(complete_document, frozen) == accepted

    def broken_renderer(*args, **kwargs):
        raise RuntimeError("untrusted renderer failed")

    monkeypatch.setattr(render, "pretty_formula", broken_renderer)
    with pytest.raises(RuntimeError, match="untrusted renderer failed"):
        render.render_proof(accepted)
    assert check(complete_document, frozen) == accepted


def test_renderer_uses_explicit_surface_ast_for_non_human_atom_names(frozen):
    from lewis_prover.render import render_proof

    data = document({"id\nwith newline": post(frozen, "B3", {"P": Atom("x\ny")})}, "id\nwith newline")
    accepted = check(data, frozen)
    rendered = render_proof(accepted)
    assert "AST " in rendered and '"op": "strict_imp"' in rendered
    assert r"x\ny" in rendered and r"id\nwith newline" in rendered
    assert len(rendered.splitlines()) == 3
    assert check(data, frozen) == accepted


@pytest.mark.parametrize("first_line", [0, -1, True, "1"])
def test_invalid_display_line_numbers_do_not_affect_checker(frozen, first_line):
    from lewis_prover.render import render_proof

    data = document({"root": post(frozen)}, "root")
    checked = check(data, frozen)
    with pytest.raises(ValueError):
        render_proof(checked, first_line=first_line)
    assert check(data, frozen) == checked
